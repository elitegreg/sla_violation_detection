'''Load new emails using helpdesk api.

This method must use the helpdesk api to load email notifications and yield
the from address and content.

Args:
    last_processed_time (datetime)

Yields:
    (str, str): fromaddr, content
'''
def load_new_emails(last_processed_time):
    # just force this to be a generator
    if False:
        yield None
