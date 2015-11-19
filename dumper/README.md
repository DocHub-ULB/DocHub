./manage.py migrate
python ./dumper/loader.py
python manage.py sqlsequencereset www documents telepathy users catalog tags | psql mydatabase
./manage.py loadtree --tree ../catalog-ulb/tree/sciences/informatique.yaml
