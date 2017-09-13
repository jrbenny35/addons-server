#!/bin/bash -x

# initialize_db:
python manage.py reset_db --noinput
python manage.py syncdb --noinput
schematic --fake src/olympia/migrations/

python manage.py loaddata initial.json
python manage.py import_prod_versions
python manage.py loaddata zadmin/users
python manage.py update_permissions_from_mc

# update_assets:
make update_assets
