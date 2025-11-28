/**
 * UI Schema System for Agentic AI
 * 
 * Agents define their UI declaratively through schemas,
 * enabling clear separation between agent logic and presentation.
 */

// Core Schema Types
export interface AgentUISchema {
  agentId: string;
  agentName: string;
  version: string;
  components: Component[];
  layout: Layout;
  actions: Action[];
  state: Record<string, any>;
}

export interface Component {
  id: string;
  type: ComponentType;
  bind?: string; // Path to agent state (e.g., "analysis.progress")
  props?: Record<string, any>;
  children?: Component[];
  style?: ComponentStyle;
}

export type ComponentType =
  | 'container'
  | 'text'
  | 'progress'
  | 'chart'
  | 'table'
  | 'form'
  | 'button'
  | 'input'
  | 'select'
  | 'checkbox'
  | 'radio'
  | 'textarea'
  | 'card'
  | 'alert'
  | 'badge'
  | 'spinner'
  | 'timeline'
  | 'tabs'
  | 'accordion';

export interface Layout {
  type: 'grid' | 'flex' | 'stack';
  columns?: number;
  gap?: number;
  direction?: 'row' | 'column';
  alignItems?: 'start' | 'center' | 'end' | 'stretch';
  justifyContent?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
}

export interface Action {
  id: string;
  label: string;
  type: 'button' | 'link' | 'submit';
  endpoint?: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  payload?: Record<string, any>;
  confirm?: boolean;
  confirmMessage?: string;
}

export interface ComponentStyle {
  width?: string | number;
  height?: string | number;
  margin?: string | number;
  padding?: string | number;
  backgroundColor?: string;
  color?: string;
  fontSize?: string | number;
  fontWeight?: string | number;
  className?: string;
}

// Component-Specific Types
export interface ProgressComponent extends Component {
  type: 'progress';
  props: {
    value: number; // 0-100
    max?: number;
    label?: string;
    showPercentage?: boolean;
    color?: 'primary' | 'success' | 'warning' | 'error';
  };
}

export interface ChartComponent extends Component {
  type: 'chart';
  props: {
    chartType: 'line' | 'bar' | 'pie' | 'scatter';
    data: any[];
    xAxis?: string;
    yAxis?: string;
    title?: string;
  };
}

export interface TableComponent extends Component {
  type: 'table';
  props: {
    columns: TableColumn[];
    data: any[];
    pagination?: boolean;
    pageSize?: number;
    sortable?: boolean;
  };
}

export interface TableColumn {
  key: string;
  label: string;
  type?: 'string' | 'number' | 'date' | 'boolean';
  sortable?: boolean;
  render?: (value: any) => string;
}

export interface FormComponent extends Component {
  type: 'form';
  props: {
    fields: FormField[];
    onSubmit?: Action;
    validation?: Record<string, any>;
  };
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: any }[];
  validation?: ValidationRule[];
}

export interface ValidationRule {
  type: 'required' | 'min' | 'max' | 'pattern' | 'email';
  value?: any;
  message?: string;
}

// Schema Builder (for agents to use)
export class UISchemaBuilder {
  private schema: Partial<AgentUISchema> = {
    components: [],
    layout: { type: 'stack' },
    actions: [],
    state: {},
  };

  constructor(agentId: string, agentName: string) {
    this.schema.agentId = agentId;
    this.schema.agentName = agentName;
    this.schema.version = '1.0.0';
  }

  addComponent(component: Component): this {
    this.schema.components!.push(component);
    return this;
  }

  setLayout(layout: Layout): this {
    this.schema.layout = layout;
    return this;
  }

  addAction(action: Action): this {
    this.schema.actions!.push(action);
    return this;
  }

  setState(state: Record<string, any>): this {
    this.schema.state = { ...this.schema.state, ...state };
    return this;
  }

  build(): AgentUISchema {
    return this.schema as AgentUISchema;
  }
}

// Example: Job Matching Agent UI Schema
export function createJobMatchingSchema(state: any): AgentUISchema {
  return new UISchemaBuilder('job-matching-agent', 'Job Matching')
    .setLayout({
      type: 'grid',
      columns: 2,
      gap: 16,
    })
    .addComponent({
      id: 'progress',
      type: 'progress',
      bind: 'analysis.progress',
      props: {
        value: state.analysis?.progress || 0,
        label: 'Analysis Progress',
        showPercentage: true,
        color: 'primary',
      },
    })
    .addComponent({
      id: 'results',
      type: 'card',
      bind: 'match.results',
      children: [
        {
          id: 'match-score',
          type: 'text',
          props: {
            content: `Match Score: ${state.match?.score || 0}%`,
            fontSize: '24px',
            fontWeight: 'bold',
          },
        },
        {
          id: 'recommendation',
          type: 'badge',
          props: {
            label: state.match?.recommendation || 'pending',
            color: state.match?.recommendation === 'proceed' ? 'success' : 'warning',
          },
        },
      ],
    })
    .addComponent({
      id: 'bias-alerts',
      type: 'alert',
      bind: 'bias.alerts',
      props: {
        severity: state.bias?.severity || 'low',
        message: state.bias?.message || '',
      },
    })
    .addAction({
      id: 'run-analysis',
      label: 'Run Analysis',
      type: 'button',
      endpoint: '/api/agents/job-matching/run',
      method: 'POST',
    })
    .setState(state)
    .build();
}

