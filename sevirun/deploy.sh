python manage.py flush --noinput && \
python manage.py migrate --noinput && \
python manage.py collectstatic --noinput && \
python manage.py loaddata users/fixtures/sample.json && \
python manage.py loaddata products/fixtures/sample.json && \
python manage.py loaddata orders/fixtures/sample.json && \
gunicorn sevirun.wsgi:application