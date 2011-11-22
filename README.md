ZeroMail
========

About
-----

[ZeroMail][1] is a Sydney based startup, working on a product to modernise email clients and inboxes.  They are hiring new Python developers, and set a small challenge to help filter out the good coders from the bad - instead (or maybe as well as) the usual application and interview process.

This repository contains my humble attempt at solving this problem.  However, I thought I'd also use it as a bit of a learning excerise, so being new to [git][2], [github][3] and Python's [setuptools/distutils][4] I have used it as an opportunity to familiarise myself with these technologies/tools.

Installation
------------

After downloading, installation is the same as most python packages, just run the setup script:

    python setup.py build
    sudo python setup.py install

Just make sure you have the [vObject][10] dependency installed.

Usage
-----

Run the script like so:

    extract -f /path/to/file/emails.txt -d dict
    extract -f /path/to/file/emails.txt -d vcard

Currently, all details are dumped to stdout.

The Problem
-----------

1. Download [emails.txt][5]
2. Write a python program that extracts contact information from the signatures in the emails.
3. That's it, submit to ZeroMail!

Initial Thoughts
----------------

After downloading the file and taking a quick skim through it's contents (all 134396 lines) a couple of things begin to stand out:

* Essentially the file is the dump of one (or maybe more) email conversations on the [Silicon Beach Australia][6] mailing list.
* There is a lot of duplication in the file - between the standard footer that Google Groups has inserted and people quoting replies we could probably cut the file in half (and so reduce the amount of processing and number of false positives) just by removing some of the duplication.
* Where are the signatures - they are definitely buried in amongst a lot of noise.
* The dump doesn't include email headers, so working out where an email starts (and so where one ends, which would help identify a possible signature) is going to be tricky.\
* The signatures vary quite a bit - they are obviously unstructured and range for a simple signoff to a full on biography.
* Most conversations include a string similar to "On 22/11/2011 Mark<mstreat...@gmail> Wrote:" - I wonder if that could be useful.

What Is a Signature?
--------------------

Sounds like a simple question, and indeed it is, but what counts as an email signature?

Well, generally speaking it is like a mini-business card which appears at the end of an email.  The sender (particularly when corresponding in a more formal context) is obliged to include more than a simple signoff such as "Thanks" or "Cheers", instead providing additional contact information (email, phone number, website, etc).

There is no standard for an email signature - it is plain, unstructured text (or occassionally HTML) and can be anything from one to 10 lines. For example, some are really long and detailed:

    Phil Sim
    Chief Executive Officer,
    MediaConnect Australia Pty Ltd
    www.mediaconnect.com.au
    philip@mediaconnect.com.au
    Ph: +61 2 9894 6277
    Fax: +61 2 8246 6383
    Mobile: 0413889940

Some are more condensed:

    Graham Lea
    Belmont Technology Pty Ltd
    graham@belmonttechnology.com.au

And some put all the information on one line:

    *Scott Purcell* | *H* smmpurcell@gmail.com | W *productivewebapps.com*

Implementation
--------------

So, how are we going to tackle this problem?  

Because the text is unstructured, and doesn't follow any particular syntax, I think a more formal parsing library (such as [Pyparsing][7] or [SPARK][8]) will be of little use here.  Something like [NLTK][9] which is more suited to natural language processing and text analysis might be of more use, however I'm not sure there is sufficient corpora or models to train the parser and even this might struggle to find the signatures given their adhoc. nature.  I've also tried to use NLTK before and struggled to make it do anything useful, so with little time to dedicate to this problem I think that might be a dead end.  So this leaves us to construct a more functional, domain specific parser just for this task.

I am reasonably confident of using some combination of regular expressions to identify the various components of the signature.  However, finding the signature in the first place is going to be the tricky part.  I think there are two approaches I can use to help with this:

1. A common string in the dump is a header inserted by the mail client, an example is given below.  Although this appears in a couple of different forms, it gives us a name and an email address.  This forms the starting point of our contact details (although this might be cheating a bit as it doesn't come from the signature), but as we know the signature will appear after (or at least contain) the authors name, I can use the name as an identifier when parsing the text to find potential sites for the signatue.

        On Jun 15, 9:06 am, Rob James <james....@gmail.com> wrote:
        On Wed, Jun 15, 2011 at 10:40 PM, Aymeric Gaurat-Apelli <aymeric@gaurat.net>wrote:

2. As the signature appears at the end of an email, we need to find where the email ends.  Using the threading might help, but more useful might be to look for typical 'signoff' words, such as "Thanks" or "Regards".  As these normally indicate the end of the email, there is a high chance they are followed by a signature.  From a quick glance at the dump, examples of diffeerent signoffs include:

        Regards
        Cheers
        Thanks
        Kind Regards
        rgds
        Best regards
        Many thanks

Output
------

The problem doesn't require the output to be in a particular format.  As we are collecting contact details, for fun (and maybe profit?) we'll output them in the vCard format (v3.0) using [vObject][10], a third party python module.

Still To Do
-----------

There are a couple of things missing that still need a little work...

1. [vObject][10] sucks a little so the resulting cards are not necessarily conformant!  For example, twitter and skype details are stuffed under email.
2. The parsing doesn't look for addresses at all.  There are a couple floating around so would be good to pick those out.
3. The code could be optimised a little - not very efficient at present.

A Note on Privacy
-----------------

This readme, and the [emails.txt][5] file that is the source of this problem contains the unencrypted contact details for a number of people.  While there is nothing particularly sensitive included in their details (there are no passwords for example) I don't have express permission to include them here.  I am assuming that by consenting to be included in the [ZeroMail][1] challenge, ZeroMail have sought the appropriate permission.

[1]: http://zeromail.com/                                   "ZeroMail"
[2]: http://git-scm.com/                                    "Git"
[3]: https://github.com/                                    "GitHub"
[4]: http://docs.python.org/distutils/index.html            "Distributing Python Modules"
[5]: http://zeromail.com/static/download/emails.txt         "emails.txt"
[6]: http://groups.google.com/group/silicon-beach-australia "Silicon Beach Australi"
[7]: http://pyparsing.wikispaces.com/                       "Pyparsing"
[8]: http://pages.cpsc.ucalgary.ca/~aycock/spark/           "SPARK"
[9]: http://www.nltk.org/                                   "NLTK"
[10]: http://vobject.skyhouseconsulting.com/usage.html      "vObject"

