# ASA Database Translation & Internationalization Guide

This documentation explains how translation and language switching works in the ASA Database project, and how to add or update translations for English and Spanish.

## Overview
- The project uses Django's built-in internationalization (i18n) system.
- All user-facing text in templates uses `{% trans %}` or `{% blocktrans %}` tags.
- The language dropdown in the header allows users to switch between English and Spanish.
- Translations are managed using `.po` files in the `locale/` directory.

## How Translation Works
1. **Template Tags**
   - Use `{% trans "Text" %}` for simple strings.
   - Use `{% blocktrans %}Text with {{ variables }}{% endblocktrans %}` for dynamic content.
   - Always add `{% load i18n %}` at the top of templates using translation tags.
2. **Language Switcher**
   - The dropdown in `base.html` posts to `/i18n/setlang/`.
   - The selected language persists via a cookie and is available as `LANGUAGE_CODE` in templates.
3. **Locale Middleware**
   - `LocaleMiddleware` in `settings.py` enables automatic language detection and switching.

## Adding or Updating Translations
1. **Mark Text for Translation**
   - In templates: `{% trans "Text" %}` or `{% blocktrans %}...{% endblocktrans %}`
   - In Python code: `from django.utils.translation import gettext as _` and use `_("Text")`
2. **Extract Messages**
   - Run: `python manage.py makemessages -l es` (for Spanish)
   - This creates/updates `locale/es/LC_MESSAGES/django.po` with all marked strings.
3. **Edit Translations**
   - Open the `.po` file and add Spanish translations for each `msgid`.
   - Example:
     ```po
     msgid "Add Specimen"
     msgstr "Agregar Especimen"
     ```
4. **Compile Translations**
   - Run: `python manage.py compilemessages`
   - This generates `.mo` files used by Django at runtime.
5. **Test Language Switching**
   - Use the dropdown to switch languages and verify translations appear.

## Best Practices
- Always use translation tags for user-facing text.
- Do not hardcode language in templates or views.
- Keep translations up to date after adding new features.
- Use `{% load i18n %}` in every template with translation tags.

## Troubleshooting
- **Missing translation:** Ensure text is marked and `.po` files are updated/compiled.
- **Dropdown not persisting:** Check `LANGUAGE_CODE` context and middleware settings.
- **TemplateSyntaxError:** Make sure `{% load i18n %}` is present and tags are used correctly.

## References
- [Django i18n documentation](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/)
- [Django makemessages](https://docs.djangoproject.com/en/5.2/ref/django-admin/#makemessages)
- [Django compilemessages](https://docs.djangoproject.com/en/5.2/ref/django-admin/#compilemessages)

---
For further help, contact the ASA Database maintainers or refer to the official Django documentation.
