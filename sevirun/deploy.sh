pip install -r requirements.txt && \
python manage.py flush --noinput && \
python manage.py migrate --noinput && \
python manage.py collectstatic --noinput && \
python manage.py loaddata sample