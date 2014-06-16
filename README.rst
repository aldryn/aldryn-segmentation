===================
Aldryn Segmentation
===================

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

> placeholder
	> Limit Block: Show first
		> Segment by Cookie: 'type' equals 'retail'
			> Text: 10% Discount offer...
		> Text: Details of offer with normal pricing...


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

> placeholder
	> Limit Block: Show first
		> Segment by Cookie: 'type' equals 'retail'
			> Text: 10% offer for French customers OR retail customers only.
		> Segment by Country: France
			> Text: 10% offer for French customers OR retail customers only.
		> Text: Normal pricing for everyone else...


An AND operation is a little more complex, but still very easy to do:

> placeholder
	> Limit Block: Show first
		> Segment by Cookie: 'type' equals 'retail'
			> Limit Block: Show first
				> Segment by Country: France
					> Text: 10% offer for French Retail Customers only.
				> Text: Normal pricing...
		> Text: Normal pricing...


An XOR operation is also straight forward:

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

