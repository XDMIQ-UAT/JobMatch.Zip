"""
Cloud Function to stop all GCP services when billing budget is exceeded.
Triggered by Pub/Sub messages from billing budget alerts.
"""
import json
import os
import base64
import logging
from typing import Dict, Any

try:
    from google.cloud import compute_v1
    from google.cloud import run_v2
except ImportError:
    # Fallback if libraries not available
    compute_v1 = None
    run_v2 = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def stop_all_services(project_id: str) -> Dict[str, Any]:
    """
    Stop all running services in the GCP project.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Dictionary with results of stopping services
    """
    stopped_services = []
    errors = []
    
    # Stop Compute Engine VMs
    if compute_v1:
        try:
            compute_client = compute_v1.InstancesClient()
            # Get all zones for the project
            zones_to_check = [
                'us-central1-a', 'us-central1-b', 'us-central1-c',
                'us-east1-a', 'us-east1-b', 'us-east1-c',
                'us-west1-a', 'us-west1-b', 'us-west1-c',
                'europe-west1-a', 'europe-west1-b', 'europe-west1-c',
                'asia-east1-a', 'asia-east1-b', 'asia-east1-c',
                'asia-southeast1-a', 'asia-southeast1-b', 'asia-southeast1-c'
            ]
            
            for zone in zones_to_check:
                try:
                    instances = compute_client.list(project=project_id, zone=zone)
                    for instance in instances:
                        if instance.status == 'RUNNING':
                            logger.info(f"Stopping VM: {instance.name} in {zone}")
                            operation = compute_client.stop(
                                project=project_id,
                                zone=zone,
                                instance=instance.name
                            )
                            stopped_services.append({
                                "type": "VM",
                                "name": instance.name,
                                "zone": zone,
                                "status": "stopped"
                            })
                except Exception as e:
                    # Zone might not exist or have no instances - this is OK
                    logger.debug(f"Zone {zone} check failed (may not exist): {e}")
        except Exception as e:
            error_msg = f"Error stopping VMs: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    else:
        logger.warning("google-cloud-compute not available")
    
    # Stop Cloud Run services (scale to 0 instances)
    if run_v2:
        try:
            run_client = run_v2.ServicesClient()
            parent = f"projects/{project_id}/locations/-"
            
            # List all Cloud Run services
            request = run_v2.ListServicesRequest(parent=parent)
            page_result = run_client.list_services(request=request)
            
            for service in page_result:
                try:
                    service_name = service.name.split('/')[-1]
                    location = service.name.split('/')[-3]
                    
                    logger.info(f"Scaling down Cloud Run service: {service_name} in {location}")
                    
                    # Update service to scale to 0
                    update_request = run_v2.UpdateServiceRequest(
                        service=service,
                        update_mask={"paths": ["template.scaling.min_instance_count", "template.scaling.max_instance_count"]}
                    )
                    
                    # Set scaling to 0
                    service.template.scaling.min_instance_count = 0
                    service.template.scaling.max_instance_count = 0
                    
                    updated_service = run_client.update_service(request=update_request)
                    stopped_services.append({
                        "type": "Cloud Run",
                        "name": service_name,
                        "location": location,
                        "status": "scaled_to_zero"
                    })
                except Exception as e:
                    error_msg = f"Error stopping Cloud Run service {service.name}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        except Exception as e:
            error_msg = f"Error listing Cloud Run services: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    else:
        logger.warning("google-cloud-run not available")
    
    return {
        "project": project_id,
        "stopped_services": stopped_services,
        "services_stopped_count": len(stopped_services),
        "errors": errors,
        "message": f"Stopped {len(stopped_services)} services due to budget limit"
    }


def stop_services_pubsub(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Cloud Function entry point for Pub/Sub trigger.
    Handles billing budget alert messages.
    
    Args:
        event: Pub/Sub event data
        context: Cloud Function context
        
    Returns:
        Result dictionary
    """
    project_id = os.environ.get('GCP_PROJECT', 'futurelink')
    
    logger.info(f"Budget alert received for project: {project_id}")
    
    # Parse Pub/Sub message
    message_data = {}
    if event.get('data'):
        try:
            decoded_data = base64.b64decode(event['data']).decode('utf-8')
            message_data = json.loads(decoded_data)
            logger.info(f"Message data: {decoded_data}")
        except Exception as e:
            logger.warning(f"Could not parse message data: {e}")
    
    # Check if this is a 100% threshold alert
    budget_amount = message_data.get('budgetAmount', {})
    cost_amount = message_data.get('costAmount', {})
    threshold_percent = message_data.get('alertThresholdExceeded', 0)
    
    logger.info(f"Budget: {budget_amount}, Cost: {cost_amount}, Threshold: {threshold_percent}")
    
    # Only stop services if threshold is 100% (or very close)
    # The budget API sends alerts at 50%, 75%, 90%, and 100%
    # We only want to stop at 100%
    if threshold_percent >= 1.0 or message_data.get('alertThresholdExceeded', 0) >= 1.0:
        logger.warning("Budget limit reached (100%)! Stopping all services...")
        result = stop_all_services(project_id)
        logger.info(json.dumps(result, indent=2))
        return result
    else:
        logger.info(f"Budget alert received but threshold ({threshold_percent}) not at 100%. No action taken.")
        return {
            "project": project_id,
            "message": f"Budget alert received at {threshold_percent*100}% threshold. Services will stop at 100%.",
            "action": "none"
        }


# For HTTP trigger (alternative)
def stop_services_http(request) -> str:
    """
    HTTP entry point for manual triggering.
    """
    project_id = os.environ.get('GCP_PROJECT', 'futurelink')
    
    # Check for authorization header or API key
    auth_header = request.headers.get('Authorization', '')
    expected_token = os.environ.get('AUTH_TOKEN', '')
    
    if expected_token and auth_header != f"Bearer {expected_token}":
        return json.dumps({"error": "Unauthorized"}), 401
    
    result = stop_all_services(project_id)
    return json.dumps(result, indent=2), 200, {'Content-Type': 'application/json'}

