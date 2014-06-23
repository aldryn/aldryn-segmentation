Aldryn Segmentation
===================

Development Status
------------------

### Segment Limter:
- [x] Limiter

### Segment Plugins:
- [x] Fallback
- [x] Segment by Switch (hard switch)
- [x] Segment by Cookie
- [x] Segment by Country
- [x] Segment by Auth Status (is authenticated)
- [x] Overridable

### Segment Pool:
- [x] Registration
- [x] De-registration
- [x] Discovery
- [x] Get override state for segment
- [x] Reset all overrides
- [x] Supports multiple operators

### Toolbar:
- [x] Displays
- [x] Working override states
- [x] Working "Reset all" option
- [x] Displays no. of overrides in Segment menu name

### Tests:

Actually, not really sure how to set-up testing for an app that one adds to
django CMS. All of the following have been performed manually via the included
test_project, however.

- [x] Segment logic tests
- [x] Segment Pool tests
- [x] I18N tests
- [x] Multiple operator tests

### Documentation:
- [ ] Operator's guide
- [ ] Developer's guide

### Other:
- [x] Move the Country Segment and its related bits to another repo?
- [x] Ensure compatibility with supported Pythons (vs. Django 1.6)
	  - [x] Python 2.6.x
      - [x] Python 2.7.x
      - [x] Python 3.3.x
      - [x] Python 3.4.x
- [x] Ensure compatibility with supported Djangos (vs. Python 2.7)
      - [x] Django 1.4.x
      - [x] Django 1.5.x
      - [x] Django 1.6.x


Known Issues
------------

This is a list of known issues that are being worked on...

- [ ] Only a partial, French translation is available, supplied by
      translate.google.com. (Mostly the rest of the country names is all that
      remains.)

- [x] Does not seem to work with the new Alias Plugin...
      Actually, its just that the AliasPlugin didn't work in Django 1.4.13.
      I've submitted a PR to fix this and added tests to help detect and
      prevent future issues.


Installation
------------

At this time, the package is not submitted to PyPi, but you can still use pip
if you like. Here's how to get started quickly:

NOTE: At this time, the project has only been tested under:
- Python 2.6, 2.7, 3.3, 3.4
- Django 1.4, 1.5, 1.6
- django CMS 3.0.2 (276fd37b0e49555bafce6c071ca50508de5e4c49 or later)

1. Make sure you're using a version of django-CMS that is later than
   3.0.2.dev1, otherwise the Segment menu will not appear correctly and likely
   the whole toolbar won't render at all.
1. If you're using Python 3, it is recommended also install:
   `pip intall pyuca` for better collation of non-EN languages.
1. `pip install https://github.com/aldryn/aldryn-segmentation/archive/master.zip`
1. Add 'segmentation' to INSTALLED_APPS in your Django project's settings file
1. `python manage.py schemamigration segmentation --initial`
1. `python manage.py migrate segmentation`

Optional, but required if you intend to run the test project included in the
repo:

1. `pip install aldryn-country-segment` (not actually in PyPI just yet), so,
   you'll need to: `pip install https://github.com/aldryn/aldryn-country-segment/archive/master.zip`
   for now.
1. Follow the instructions provided in the README for Aldryn Country Segment.

At this point you should be good to go. When you next run your project, the
first thing you may notice is that you have new–albeit empty–'Segments' menu
in your toolbar.


Basic Usage
-----------

To use segmentation, you simply add Segmentation plugins into your
placeholders. The most important one is the Segment Limit plugin. This serves
as a container for all other segment plugins. Once you add a Limit plugin to a
placeholder, you'll then notice you have other plugins that you can then
install as children to the limit plugin.


Description
-----------

This django CMS application allows the CMS operator to display different
content to different "segments" of visitors.

By using different Segmentation Plugins, the CMS operator can define segments
which meet certain criteria, such as:

* Authenticated: Visitor has a valid session
* Retail Customer: Visitor presented a cookie named 'customer_type' with a
  value of 'retail'
* Offer Valid in Region: Visitor's IP address is thought to be in France

In addition, in order to aide the operator in providing "Fallbacks" when
conditions aren't met and other scenarios, this application provides a
"Segmentation Limit Block" plugin, which can be used to limit the number of
matching conditions that will display in any given placeholder.

Combining a segment plugin with a segmentation limit block plugin, arbitrarily
complex logical conditions can be described. Here's the basics:

"Show details of 10% discount offer to retail customers only."

````
	> placeholder
		> Limit Block: Show first
			> Segment by Cookie: 'type' equals 'retail'
				> Text: 10% Discount offer...
			> Text: Details of offer with normal pricing...
````

In this example, the Limit Block will only allow one of its children to be
displayed. If the Segment by Cookie plugin is triggered because the visitor
has a cookie named 'type' with a value of 'retail', then the Segement by
Cookie's children (all of them) will be displayed.

If the visitor does not have a 'type' cookie, or it does not contain 'retail',
then the Segment by Cookie plugin will not be considered for rendering, nor
will any of its children. This will then permit consideration of the next
child to the limit block. In this case, it is a normal, non-segment plugin
that will "count" for the limit of 1 and will be rendered.

In a similar manner, multiple conditions can be considered and combined with
AND, OR or XOR operations as required. Here's an OR operation:

````
	> placeholder
		> Limit Block: Show first
			> Segment by Cookie: 'type' equals 'retail'
				> Text: 10% offer for French customers OR retail customers only.
			> Segment by Country: France
				> Text: 10% offer for French customers OR retail customers only.
			> Text: Normal pricing for everyone else...
````

An AND operation is a little more complex, but still very easy to do:

````
	> placeholder
		> Limit Block: Show first
			> Segment by Cookie: 'type' equals 'retail'
				> Limit Block: Show first
					> Segment by Country: France
						> Text: 10% offer for French Retail Customers only.
					> Text: Normal pricing...
			> Text: Normal pricing...
````

An XOR operation is also straight forward:

````
	> placeholder
		> Limit Block: Show first
			> Segment by Cookie: 'type' equals 'retail'
				> Limit Block: Show first
					> Segment by Country: France
						> Text: Normal pricing...
					> Text: 10% offer for French customers OR retail customers only
					        (but not French retail customers).
			> Segment by Country: France
				> Limit Block: Show first
					> Segment by Cookie: 'type' equals 'retail'
						> Text: Normal pricing...
					> Text: 10% offer for French customers OR retail customers only
					        (but not French retail customers).
			> Text: Normal pricing...
````
