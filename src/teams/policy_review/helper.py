from datetime import datetime, timedelta

# Function tp check claim notification period
def check_claim_notification_period(claim_report_date_str, notification_period):
    # Parse the claim report date
    claim_report_date = datetime.strptime(claim_report_date_str, "%B %d %Y")
    
    # Use current date as reference
    current_date = datetime.now()
    
    # Calculate notification deadline
    notification_deadline = current_date - timedelta(days=notification_period)
    
    # Check if claim was reported within notification period
    is_within_period = claim_report_date >= notification_deadline
    
    return {
        'is_within_notification_period': is_within_period,
        'notification_period': notification_period,
        'days_since_report': (current_date - claim_report_date).days
    }
