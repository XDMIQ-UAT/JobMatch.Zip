param(
  [Parameter(Mandatory=$true)][string]$To,
  [Parameter(Mandatory=$false)][string]$Body = "Test from JobFinder automation"
)

# Default sender (your Twilio number)
$From = "+18444842922"

function Convert-ToE164 {
  param([string]$Number)
  $digits = ($Number -replace "[^0-9]", "")
  if ($digits.Length -eq 10) { return "+1$digits" }
  elseif ($digits.Length -eq 11 -and $digits.StartsWith("1")) { return "+$digits" }
  elseif ($Number.StartsWith("+")) { return $Number }
  else { return "+$digits" }
}

$toE164 = Convert-ToE164 -Number $To

Write-Host "Sending SMS to $toE164 from $From..."

# Uses active Twilio CLI profile (created via `twilio login`)
$exit = twilio api:core:messages:create --from "$From" --to "$toE164" --body "$Body"
exit $LASTEXITCODE
