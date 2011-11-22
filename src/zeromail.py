#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 Mark Streatfield <mstreatfield@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import with_statement

import re
import vobject

# Some useful constants.
THREAD_IDENTIFIER = ">"
HIGH_FREQUENCY_THRESHOLD = 90
POSSIBLE_SIGNOFFS = [
                     "regards", 
                     "cheers", 
                     "thanks", 
                     "kind regards", 
                     "rgds", 
                     "best regards", 
                     "many thanks"
                    ]

# Compile some regular expressions that we know we're going to use frequently 
# later on in the code.
EMAIL_HEADER_REGEX = re.compile("(?P<name>[a-zA-Z][a-zA-Z0-9 ]+) <(?P<email>[a-zA-Z0-9.-_]+[a-zA-Z0-9-_]@[a-zA-Z0-9._-]+.[a-zA-Z0-9._-]+)> wrote:")
RELAXED_HEADER_REGEX = re.compile("(?P<name>[a-zA-Z][a-zA-Z0-9 ]+) <?(?P<email>[a-zA-Z0-9.-_]+@[a-zA-Z0-9._-]+.[a-zA-Z0-9._-]+)>? (wrote:)?")
SKYPE_USERNAME_REGEX = re.compile("[Ss]kype:\s*(?P<skype>[a-zA-Z][a-zA-Z0-9-_,.]{5,32})") # http://forum.skype.com/index.php?showtopic=527951
TWITTER_USERNAME_REGEX = re.compile("([Tt]witter.*:|(?=^@))\s*(?P<twitter>@?[a-zA-Z_.]{1,15})") #
PHONE_REGEX_STRING = """
    (?P<type>([a-zA-Z:()./ *]+)|^)\s*(?P<number>
    ([0-9]{4}\s[0-9]{3}\s[0-9]{3})|
    (\+[0-9]{2}\s[0-9]\s[0-9]{4}\s[0-9]{4})|
    ([0-9]{10})|
    (\(\+[0-9]{2}\)\s[0-9]{4}\s[0-9]{3}\s[0-9]{3})|
    (\+\s[0-9]{2}\s\([0-9]\)\s[0-9]{3}\s[0-9]{3}\s[0-9]{3})|
    ([0-9]{4}\s[0-9]{3}\s[0-9]{3})|
    ([0-9]{4}\s[0-9]{6})|
    (\+[0-9]{2}\s[0-9]{3}\s[0-9]{3}\s[0-9]{3})|
    (\+[0-9]{11})|
    ([0-9]\.[0-9]{3}\.[0-9]{3}\.[0-9]{4})|
    ([0-9]{4}\s[0-9]\s[0-9]{5})|
    ([0-9]{3}\.[0-9]{3}\.[0-9]{4})|
    ([0-9]{4}\.[0-9]{3}\.[0-9]{3})|
    ([0-9]{4}\s[0-9]{3}\s[0-9]{3})|
    ([0-9]{2}\s[0-9]{4}\s[0-9]{4})|
    ([0-9]{4}\s[0-9]{4})|
    (\([0-9]{2}\)\s[0-9]{4}\s[0-9]{4})
)"""
PHONE_REGEX = re.compile(PHONE_REGEX_STRING, re.X) # OK, THIS ONE IS LAME (but I am bored now).
EMAIL_REGEX = re.compile("(?P<email>[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+\.[a-zA-Z]+)")
URL_RE = re.compile("(?P<url>((https?://)|(www\.))?[a-zA-Z]+\.[a-zA-Z./]+)")

class STATES(object):
    """
    A simple enum.
    """
    
    OUTSIDE_SIGNATURE, INSIDE_SIGNATURE = range(0, 2)

class Contact(object):
    """
    Class for storing out contact details.
    """
    
    def __init__(self, **kwargs):
        """
        Initialise the object.
        """
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        
        return "<Contact %s>" % " ".join(["%s -> %s" % (key, getattr(self, key)) for key in ("firstname", "lastname") if hasattr(self, key)])
    
    def dump(self, format="vcard"):
        """
        Make a vCard for this contact.
        """
        
        if format in "vcard":
            return self._dump_vcard()
        
        elif format in "dict":
            return self._dump_dict()
        
        raise Exception("Other formats not yet supported, please only use vcard or dict")
    
    def _dump_dict(self):
        """
        Dump contact to some custom pprint format
        """
        
        data = {}
        
        for attribute in ("skype", "twitter", "email", "url", "phone", "firstname", "lastname", "othernames"):
            data[attribute] = None
            
            if hasattr(self, attribute):
                data[attribute] = getattr(self, attribute)
        
        return data
    
    def _dump_vcard(self):
        """
        Make a vcard representation of this contact.
        
        :return:
            String/buffer serialisation of the vcard.
        """
        
        card = vobject.vCard()
        
        card.add("n")
        card.n.value = vobject.vcard.Name(family=self.lastname, given=self.firstname)
        
        card.add('fn')
        card.fn.value = "%s %s %s" % (self.firstname, self.othernames, self.lastname)
        
        for attribute in ("skype", "twitter"):
            if hasattr(self, attribute):
                content = vobject.vcard.ContentLine("EMAIL", {}, getattr(self, attribute))
                card.add(content)
        
        for attribute in ("email", "url", "phone"):
            if hasattr(self, attribute):
                for value in getattr(self, attribute):
                    if attribute == "phone":
                        content = vobject.vcard.ContentLine("TEL", {}, value["number"])
                    elif attribute == "email":
                        content = vobject.vcard.ContentLine("EMAIL", {}, value)
                    elif attribute == "url":
                        content = vobject.vcard.ContentLine("URL", {}, value)
                
                card.add(content)
        
        return card.serialize()

class ContactsList(list):
    """
    Utility class for storing a list of contacts.
    """
    
    def add(self, contact):
        """
        Add a new contact to the list.
        
        :param contact:
            An instance of :class:`Contact`.
        """
        
        self.append(contact)
    
    def search(self, **kwargs):
        """
        Very basic search function to pull out matching
        contacts.  Exact string matching only, arguments are AND together.
        
        Looks for each keyword argument as an attribute on every
        contact.  If attribute exists, and is exact match, bingo!
        
        :returns:
            A list of contacts!
        """
        
        matches = []
        
        for contact in self:
            if all([(hasattr(contact, key) and getattr(contact, key) == value) for key, value in kwargs.items()]):
                matches.append(contact)
        
        return matches

class Extractor(object):
    """
    Class for extacting email signatures from a dump of emails.
    """
    
    def __init__(self):
        """
        Initialise the object.
        """
        
        self._lines = [] # Define variable for holding the file contents.
        self._contacts = ContactsList() # Define variable for holding the contacts that we find.
    
    def load(self, filename):
        """
        Read the contents of the file.  This file (for example data/emails.txt)
        should be the file we wish to extract signatures from.
        
        .. warning::
            This is potentially inefficient as we read the entire file in in one
            go and keep it in memory.  We might wish to restructure this to use 
            an iterator to keep less of the file in memory, however this might
            break parts of the algorithm.
        
        :param filename:
            The name of the file on disk to load.
        """
        
        with open(filename) as fd:
            self._lines = fd.readlines()
    
    def _remove_thread_lines(self):
        """
        Remove thread lines from the input.  A thread is deemed to be any line 
        starting with a '>' character.
        """
        
        self._lines = [line for line in self._lines if not line.startswith(THREAD_IDENTIFIER)]
    
    def _remove_duplicate_lines(self):
        """
        Remove duplicate (or high frequency) lines from the input.  A duplicate, 
        or high frequency line, is a line that appears more than 90 times in 
        the content
        """
        
        def histogram(in_):
            """
            Return a histogram of values from the input data.
            
            Could use a collections.Counter in Python2.7 if we so wished...
            
            :param in_:
                A list of data.
            :returns:
                A dictionary, keyed by the line, value is occurence count.
            """
            
            hist = {}
            for value in in_ and value not in hist:
                hist[value] = in_.count(value)
            
            return hist
        
        frequency = histogram(self._lines)
        
        # Remove lines that appear too often.
        for value, count in frequency.iteritems():
            if count >= HIGH_FREQUENCY_THRESHOLD:
                self._remove_lines(value)
    
    def _remove_lines(self, in_):
        """
        Remove all occurences of the given line from the inputted content.
        
        :param in_:
            A line from the file.
        """
        
        self._lines = [line for line in self._lines if line != in_]
    
    def parse(self, ignore_threads=True, remove_duplicate=False):
        """
        Main method for parsing the contents of the file (which must have been
        previously loaded through a call to the :meth:`load` method.
        
        .. warning::
            This is potentially inefficient as we read the :attr:`_lines` variable 
            multiple times.  For large files this might be costly, consider
            restructuring.
        
        :param ignore_threads:
            By default, threads will be ignored from the input.  A thread is 
            deemed to be any line starting with a '>' character.
        :param remove_duplicate:
            By default, duplicate (or high frequency) lines will not be removed 
            from the input.
        """
        
        if not self._lines:
            raise Exception("A file must be loaded first using the load method.")
        
        if ignore_threads:
            self._remove_thread_lines()
        
        if remove_duplicate:
            self._remove_duplicate_lines()
        
        # This will populate our contacts list with some names that will then help us 
        # find signatures later.
        self._find_names()
        
        # Find the signatures!  Yay!
        self._find_signatures()
    
    def _find_names(self):
        """
        Search for email headers in inputted content to help identify potential 
        signatures later on in our processing.
        
        A header is of the form:
            On Jun 15, 9:06 am, Rob James <james@gmail.com> wrote:
        """
        
        for line in self._lines:
            match = re.search(EMAIL_HEADER_REGEX, line)
            
            if match:
                groups = match.groupdict()
                
                # We don't care about emails which aren't fully formed.  Some of 
                # the emails contain ellipses '...' which is no use to us, for example:
                # On Jun 15, 9:06 am, Rob James <james....@gmail.com> wrote:
                # I thought I could not match these using a negative lookahead assetion 
                # in the regex, but that either doesn't do what I think, or I am using
                # it incorrectly as we still pick them up.  We filter them out here.
                email = groups["email"]
                if "..." in email:
                    continue
                
                # Pull out the first, last and other names.
                name = groups["name"].split()
                first = name[0]
                last = name[-1] if len(name) >= 2 else ""
                other = " ".join(name[1:-1]) if len(name) > 2 else ""
                
                # We have our first contact!  Add it to our list of contacts if we don't
                # have it already.
                if not self._contacts.search(firstname=first, lastname=last, othernames=other, email=[email]):
                    contact = Contact(firstname=first, lastname=last, othernames=other, email=[email])
                    self._contacts.add(contact)
    
    def _find_signatures(self):
        """
        Search for signatures using various helpers and extract the contact information,
        add this to our contact list!
        
        This is kinda like a mini state machine I guess.  Could be expanded to a more formal
        one.
        
        .. todo::
            Still lots of work to be done here to improve things.  A confidence rating might help
            to help identify signatures, better use of the signoff etc. etc.
        """
        
        # Some useful limits.
        SIGNOFF_LINE_LENGTH_LIMIT = 3
        SIGNATURE_LINE_LENGTH_LIMIT = 10
        SIGNATURE_LINE_COUNT_LIMIT = 15
        
        # Manage the state.
        CURRENT_STATE = STATES.OUTSIDE_SIGNATURE
        FOUND_CONTACT = None
        SIGNATURE_LINE_COUNT = 0
        
        for line in self._lines:
            # Perhaps these lines should be cleared out earlier?
            if not line.strip():
                continue
            
            if CURRENT_STATE == STATES.OUTSIDE_SIGNATURE:
                # If we are in this state, then we are trying to find a signature, or the
                # start of one.  Given we know the signature comes at the end of the email, 
                # after a signoff string or a name, we know we only need consider:
                #    * lines which are short - not a full sentence, so anything more than a 
                #      few words can be ignored.
                #    * lines which contain a signoff.
                #    * lines which contain a name we found earlier in our call to :meth:`_find_names`.
                tokens = line.split()
                if len(tokens) > SIGNOFF_LINE_LENGTH_LIMIT:
                    continue
                
                # Perhaps the line contains a name... let's try and find it.
                first = tokens[0]
                last = tokens[-1] if len(tokens) >= 2 else ""
                
                matches = self._contacts.search(firstname=first)
                if len(matches) == 0:
                    # No contact found, perhaps it wasn't a name after all...
                    if line.lower() in POSSIBLE_SIGNOFFS:
                        # It's a signoff string, should give us confidence we are 
                        # getting close to the signature....
                        pass
                    
                    continue
                
                elif len(matches) > 1:
                    # More than one match found, perhaps we can match on lastname too?
                    matches = self._contacts.search(firstname=first, lastname=last)
                    
                    # If we still have more than one match, then we have ambiguity.
                    # Can't think of a way to resolve this right now.
                    if len(matches) != 1:
                        #print "AMBIG", first, "**",last,"**", tokens, line
                        continue
                    
                    # If we get this far, we have one match only, we can't match 0 contacts
                    # as otherwise we wouldn't have entered this block to begin with.
                
                # Yay, we found a match, assume that means a signature is coming next.
                CURRENT_STATE = STATES.INSIDE_SIGNATURE
                FOUND_CONTACT = matches[0]
            
            elif CURRENT_STATE == STATES.INSIDE_SIGNATURE:
                SIGNATURE_LINE_COUNT += 1
                
                # Ok, we think we are inside a signature, time to parse out all the details.
                tokens = line.split()
                
                # If the line is too long, it is possible we have dropped out of the signature,
                # so change state...
                if len(tokens) > SIGNATURE_LINE_LENGTH_LIMIT:
                    CURRENT_STATE = STATES.OUTSIDE_SIGNATURE
                    FOUND_CONTACT = None
                    SIGNATURE_LINE_COUNT = 0
                    continue
                
                # Or, if we have been inside a signature for a while now, perhaps it's time to
                # bail out...
                if SIGNATURE_LINE_COUNT > SIGNATURE_LINE_COUNT_LIMIT:
                    CURRENT_STATE = STATES.OUTSIDE_SIGNATURE
                    FOUND_CONTACT = None
                    SIGNATURE_LINE_COUNT = 0
                    continue
                
                # We are still picking up lines that look like:
                #    On Oct 20, 11:12 am, drllau <drlawrence...@gmail.com> wrote:
                # So we force those to disappear!  We also know that if we found one, we have
                # reached the end of our signature.
                if re.search(RELAXED_HEADER_REGEX, line) or "..." in line:
                    CURRENT_STATE = STATES.OUTSIDE_SIGNATURE
                    FOUND_CONTACT = None
                    SIGNATURE_LINE_COUNT = 0
                    continue
                
                # So, we got this far, we think we have a signature!!  Let's do some matching...
                # First, let's look for a skype name, this is nice and simple.
                skype = self._match_skype(line)
                if skype:
                    FOUND_CONTACT.skype = skype
                    # Don't look for anything else!
                    continue
                
                # Next we look for twitter as that is also quite simple.  
                twitter = self._match_twitter(line)
                if twitter:
                    FOUND_CONTACT.twitter = twitter
                    # Don't look for anything else!
                    continue
                
                # Next we look for a phone number, and we know there might be more than one on
                # a line, so...
                numbers = self._match_phone(line)
                if numbers:
                    # We might have more than one phone number so we store a list.
                    if not hasattr(FOUND_CONTACT, "phone"):
                        FOUND_CONTACT.phone = []
                    
                    # And this time we store the phone number as a dict.
                    for number in numbers:
                        if number not in FOUND_CONTACT.phone:
                            FOUND_CONTACT.phone.append(number)
                
                # Now look for an email address...
                email = self._match_email(line)
                if email:
                    # We might have more than one email so we store a list.
                    if not hasattr(FOUND_CONTACT, "email"):
                        FOUND_CONTACT.email = []
                    
                    if email not in FOUND_CONTACT.email:
                        FOUND_CONTACT.email.append(email)
                
                # And last but not least, look for a url... 
                url = self._match_url(line)
                if url and "@" not in url:
                    # We might have more than one url so we store a list.
                    if not hasattr(FOUND_CONTACT, "url"):
                        FOUND_CONTACT.url = []
                    
                    if url not in FOUND_CONTACT.url:
                        FOUND_CONTACT.url.append(url)
    
    def _match_skype(self, line):
        skype_match = re.search(SKYPE_USERNAME_REGEX, line)
        if skype_match:
            return skype_match.groupdict()["skype"]
    
    def _match_twitter(self, line):
        twit_match = re.search(TWITTER_USERNAME_REGEX, line)
        if twit_match:
            return twit_match.groupdict()["twitter"]
    
    def _match_phone(self, line):
        def find_phone_number_type(in_):
            """
            Function to try and work out what type of phone number we have...
            """
            
            if in_ in ("(M) ", "Cell/Mobile: ", "m: ", "Mobile: ", " M "):
                return "mobile"
            
            if in_ in ("(F) ", "f: ", "Fax: ", " F "):
                return "fax"
            
            return "work"
        
        numbers = []
        
        for phone_match in re.finditer(PHONE_REGEX, line):
            number_type = find_phone_number_type(phone_match.groupdict()["type"])
            number = {"type":number_type, "number":phone_match.groupdict()["number"]}
            
            if number not in numbers:
                numbers.append(number)
        
        return numbers
    
    def _match_email(self, line):
        email_match = re.search(EMAIL_REGEX, line)
        if email_match:
            return email_match.groupdict()["email"]
    
    def _match_url(self, line):
        url_match = re.search(URL_RE, line)
        if url_match:
            return url_match.groupdict()["url"]
    
    def dump(self, format):
        """
        Dump all the contacts we have found to a vCard format!
        """
        
        for contact in self._contacts:
            print contact.dump(format=format)
