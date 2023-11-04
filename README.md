# In reference to issue 11130 on the Wagtail project

https://github.com/wagtail/wagtail/issues/11130



### Issue Summary

When overriding the `wagtail.admin.panels.InlinePanel` class's child_edit_handler property; the returned MultiFieldPanel does not honor the `collapsed` class in the templates. I'd like to be able to individually collapse the subpanels of the `InlinePanel`; this provides a better overview while not taking up too much screenspace.

### Steps to Reproduce

1. Override the panel class like so:

```
class InlineOfficeHoursPanel(InlinePanel):
    def __init__(self, *args, **kwargs):
        kwargs["min_num"] = 7
        kwargs["max_num"] = 7
        super().__init__(*args, **kwargs)

    @cached_property
    def child_edit_handler(self):
        panels = self.panel_definitions
        child_edit_handler = MultiFieldPanel(panels, heading=self.heading, classname="collapsible collapsed")
        return child_edit_handler.bind_to_model(self.db_field.related_model)

    class BoundPanel(InlinePanel.BoundPanel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for index, child in enumerate(self.children):
                child: MultiFieldPanel.BoundPanel

                print(child.classname) # does print "collapsible collapsed".

                ....

```

2. Define the panel on any model with a relationship suited for InlinePanel.
3. Go to the wagtailadmin settings section, click on the office menu item and look at the panel.

Expected result:
![image](https://github.com/wagtail/wagtail/assets/91429854/015ad5cd-b7dd-4a21-8723-1a2149d111c6)

Actual results:
![image](https://github.com/wagtail/wagtail/assets/91429854/479e2e44-5a69-42d8-b4a2-564a6e5dafc7)

#### Any other relevant information.

Though this might not be the conventional way of customising wagtail; it is and remains a Panel. The expectation would be for this to work. Though I don't know how complex logic for this would be; I suspect it would be just as easy as with the `heading` attribute.
Going through the `components/InlinePanel.ts` makes me _think_ more attributes are not supported; but I don't know Typescript all too well; and don't understand the intricacies of how panels are set up all too well.

- I have confirmed that this issue can be reproduced as described on a fresh Wagtail project: **yes**

### Technical details

- Wagtail version: 5.1.3
