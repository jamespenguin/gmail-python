#!/usr/bin/env python
#
# GMail Web Interface API
# By Brandon Smith (brandon.smith@gmail.com)
#
import time, sys
import socket, httplib, urllib, urllib2
import BeautifulSoup, MultipartPostHandler
import form_grabber

###
# Config
###
GMAIL_URL = "http://google.com/mail"
HTML_INBOX_URL = "https://mail.google.com/mail/?ui=html&zy=a"
IMAP_SERVER = "imap.googlemail.com"
IMAP_PORT = 587
MAX_RETRIES = 5

#!# End Config #!#

class session:
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(),
                                             MultipartPostHandler.MultipartPostHandler())
        self.__opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')]
        self.__logged_in = False

    def __get_doc(self, url, data=None):
        """
        Return HTML string contents of a given URL
        """
        for i in range(0, MAX_RETRIES):
            try:
                if data:
                    page = self.__opener.open(url, data).read()
                else:
                    page = self.__opener.open(url).read()
                return page
            except urllib2.URLError:
                time.sleep(3)
            except httplib.BadStatusLine or httplib.InvalidURL:
                time.sleep(3)
            except socket.error or socket.timeout:
                time.sleep(3)
            except:
                import traceback
                traceback.print_exc()
                count += 1
        raise NameError("Failed to grab URL: %s", url)

    def login(self):
        """
        Log in to GMail
        Returns True if successful, or False if unsuccessful
        """

        # Grab the login page, and then parse out the FORM data
        page = self.__get_doc(GMAIL_URL)
        action_url, data = form_grabber.process_form(page, GMAIL_URL)
        data["Email"] = self.__username
        data["Passwd"] = self.__password

        # Prepare the login request and try logging in
        data = urllib.urlencode(data)
        request = urllib2.Request(action_url, data)
        response = self.__get_doc(request)

        # Process the server's response
        if "Sign out" not in response:
            return False
        self.__logged_in = True

        return True

    def get_messages(self, unread_only=False):
        """
        Retrieve messages from inbox.
        """
        if not self.__logged_in:
            self.login()

        # Get inbox page
        page = self.__get_doc(HTML_INBOX_URL)
        soup = BeautifulSoup.BeautifulSoup(page)

        # get the session url
        session_url = ""
        for tag in soup.findAll("link"):
            if not tag.has_key("rel") or tag["rel"] != "stylesheet":
                continue
            session_url = tag["href"]
            session_url = session_url.split("?")[0]

        # Get messages
        messages = []
        inbox_table = soup.findAll("table")[6]
        inbox_table = inbox_table.findAll("table")[1]
        for row in inbox_table.findAll("tr"):
            message = {}
            for column in row.findAll("td")[1:3]:
                # Parse for from name
                if column.has_key("width") and column["width"] == "25%":
                    if column.findAll("b"):
                        message["is_unread"] = False
                        message["from_name"] = column.findAll("b")[0].string
                    else:
                        message["is_unread"] = False
                        message["from_name"]= column.string
                elif not column.findAll("a"):
                    message["is_unread"] = True
                    message["from_name"] = column.findAll("b")[0].string
                else:
                    # parse for other stuff
                    link_section = column.findAll("a")[0]
                    message_link = link_section["href"]
                    message_link = urllib2.urlparse.urljoin(session_url, message_link)
                    message["message_link"] = message_link
                    # yes this is dirty, don't judge me.
                    subject = str(link_section).split("\n")[3]
                    subsoup = BeautifulSoup.BeautifulSoup(subject)
                    if subsoup.findAll("b"):
                        subject = subsoup.findAll("b")[0].string
                    message["subject"] = subject

            if not message:
                continue
            if unread_only and not message["is_unread"]:
                continue
            if message not in messages:
                messages.append(message)

        return messages

    def send_message(self, to_addr, message_subject, message_body):
        """
        Send an email!
        Returns true if was successful
        """
        if not self.__logged_in:
            self.login()

        # Get inbox page
        page = self.__get_doc(HTML_INBOX_URL)
        soup = BeautifulSoup.BeautifulSoup(page)

        # Get the compose url
        session_url = ""
        for tag in soup.findAll("link"):
            if not tag.has_key("rel") or tag["rel"] != "stylesheet":
                continue
            session_url = tag["href"]
            session_url = session_url.split("?")[0]
        compose_url = urllib2.urlparse.urljoin(session_url, "?v=b&pv=tl&cs=b")

        # Get compose page
        page = self.__get_doc(compose_url)
        soup = BeautifulSoup.BeautifulSoup(page)

        # Get the session url again
        session_url = ""
        for tag in soup.findAll("link"):
            if not tag.has_key("rel") or tag["rel"] != "stylesheet":
                continue
            session_url = tag["href"]
            session_url = session_url.split("?")[0]

        # set POST data
        action_url, data = form_grabber.process_form(page, session_url, form_index=1)
        data["to"] = to_addr
        data["subject"] = message_subject
        data["body"] = message_body
        data["nvp_bu_send"] = "Send"

        # send the message
        request = urllib2.Request(action_url)
        response = self.__get_doc(request, data)
        if "Your message has been sent." not in response:
            return False
        return True

    def get_message_contents(self, message_url):
        """
        Return the message body contents for a given message URL
        """
        if not self.__logged_in:
            self.login()

        # get message page
        page = self.__get_doc(message_url)
        soup = BeautifulSoup.BeautifulSoup(page)

        # get message body
        for tag in soup.findAll("div"):
            if not tag.has_key("class") or tag["class"] != "msg":
                continue
            return str(tag)