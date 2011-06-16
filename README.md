GMail-Python
============

GMail-Python is a Python module for interacting with GMail's web interface in Python.

Operations Currently Supported
------------------------------

* Grab messages in inbox
* Send messages

TODO
----

* Add support for getting message contents
* More functions that rock
* Better documentation

Usage Examples
--------------

Get all messages in the inbox, and print their info

    import gmail.GMail
    
    username = "bruce.lee"
    password = "kapow!"
    session = gmail.session(username, password)
    session.login()
    
    messages = session.get_messages()
    for message in messages:
        print "-" * 50
        print "Message Details:"
        print "From: %s" % message["from_name"]
        print "subject: %s" % message["subject"]
        print "is unread: %s" % message["is_unread"]
        print "message URL: %s" % message["message_link"]

