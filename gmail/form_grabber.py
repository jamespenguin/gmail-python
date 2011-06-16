#!/usr/bin/env python
#
# HTML Form Parsing Tool
# By Brandon Smith (brandon.smith@studiobebop.net)
#
import BeautifulSoup

def __get_base_url(url):
    protocol  = url.split("://")[0]
    url = url.split("://")[1]
    url = url.split("/")
    url = "/".join(url[:len(url)-1])
    if not url.endswith("/"):
        url += "/"
    return "%s://%s" % (protocol, url)

def __get_root_url(url):
    protocol  = url.split("://")[0]
    url = url.split("://")[1]
    url = url.split("/")[0]
    if url.endswith("/"):
        url = url[:len(url)-1]
    return "%s://%s" % (protocol, url)

def process_form(page, current_url, form_index=0, debug=False):
    root_url = __get_root_url(current_url)
    base_url = __get_base_url(current_url)

    # Process input form(s)
    soup = BeautifulSoup.BeautifulSoup(page)
    forms = soup.findAll("form")
    if not forms:
        forms = soup.findAll("FORM")
    form = str(forms[form_index])

    try:
        action = form.split("action=\"")[1].split("\"")[0]
    except:
        action = form.split("ACTION=\"")[1].split("\"")[0]
    action = action.replace("&amp;", "&")
    if not action:
        action = current_url
    if not action.startswith("http"):
        if action.startswith("/"):
            action = root_url + action
        else:
            action = base_url + action

    # parse inputs
    input_data = []
    soup = BeautifulSoup.BeautifulSoup(form)

    inputs = soup.findAll("textarea")
    for input in inputs:
        input = str(input)
        input_type = "text"
        input_value = ""

        try:
            input_name = input.split("name=")[1].split()[0]
        except:
            try:
                input_name = input.split("NAME=")[1].split()[0]
            except:
                input_name = ""
        input_name = input_name.replace("\"", "")
        input_name = input_name.replace("'", "")
        input_id = input_name

        input_data.append([input_type, input_name, input_id, input_value])

    inputs = soup.findAll("input")
    for input in inputs:
        input = str(input)
        try:
            input_type = input.split("type=")[1].split()[0]
        except:
            try:
                input_type = input.split("TYPE=")[1].split()[0]
            except:
                c = re.compile("textfield", re.I)
                if c.search(input):
                    input_type = "text"
        input_type = input_type.replace("\"", "")
        input_type = input_type.replace("'", "")
        input_type = input_type.lower()
        if input_type in ["button", "submit", "radio", "image", "checkbox"]:
            continue

        try:
            input_name = input.split("name=")[1].split()[0]
        except:
            try:
                input_name = input.split("NAME=")[1].split()[0]
            except:
                input_name = ""
        try:
            input_id = input.split("id=")[1].split()[0]
        except:
            try:
                input_id = input.split("ID=")[1].split()[0]
            except:
                input_id = ""
        input_name = input_name.replace("\"", "")
        input_name = input_name.replace("'", "")
        input_id = input_id.replace("\"", "")
        input_id = input_id.replace("'", "")

        try:
            input_value = input.split("value=\"")[1].split("\"")[0]
        except:
            try:
                input_value = input.split("VALUE=\"")[1].split("\"")[0]
            except:
                input_value = ""
        input_value = input_value.replace("&amp;", "&")

        input_data.append([input_type, input_name, input_id, input_value])

    # build request dictionary
    data = {}
    for input_type, input_name, input_id, input_value in input_data:
        data[input_name] = input_value

    if debug:
        print "[+] Action URL: %s" % action
        print "[+] POST Data"
        for key in data.keys():
            print "[+] '%s' => '%s'" % (key, data[key])

    return action, data