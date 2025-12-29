import pymysql
import pymysql.cursors
from django.core.management.base import BaseCommand
from django.db import transaction
from properties.models import District, Local

class Command(BaseCommand):
    help = 'Import District and Local data from MariaDB purchasing database'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, default='localhost')
        parser.add_argument('--port', type=int, default=3307)
        parser.add_argument('--user', type=str, default='p7user')
        parser.add_argument('--password', type=str, default='P7*123fyminc!')
        parser.add_argument('--database', type=str, default='purchasing')

    def handle(self, *args, **options):
        self.stdout.write("Connecting to MariaDB...")
        
        try:
            conn = pymysql.connect(
                host=options['host'],
                port=options['port'],
                user=options['user'],
                password=options['password'],
                database=options['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            self.stdout.write(self.style.SUCCESS("Connected to MariaDB!"))

            # Import Districts
            self.stdout.write("Fetching 'district' table...")
            cursor.execute("SELECT * FROM district")
            districts_data = cursor.fetchall()
            
            with transaction.atomic():
                d_count = 0
                for row in districts_data:
                    # Specific mapping found via inspection:
                    # MariaDB district: dcode, distname
                    # Django District: dcode, name
                    dcode = row.get('dcode')
                    name = row.get('distname')
                    
                    if dcode and name:
                        District.objects.update_or_create(
                            dcode=dcode,
                            defaults={'name': name}
                        )
                        d_count += 1
                
                self.stdout.write(self.style.SUCCESS(f"Imported/Updated {d_count} Districts."))

                # Import Locals (lokal2)
                self.stdout.write("Fetching 'lokal2' table...")
                cursor.execute("SELECT * FROM lokal2")
                locals_data = cursor.fetchall()
                
                l_count = 0
                for row in locals_data:
                    # Specific mapping found via inspection:
                    # MariaDB lokal2: dcode, lcode, lokal
                    # Django Local: lcode, name, district (fk)
                    lcode = row.get('lcode')
                    name = row.get('lokal')
                    dcode_ref = row.get('dcode')
                    
                    if lcode and name and dcode_ref:
                        try:
                            dist = District.objects.get(dcode=dcode_ref)
                            Local.objects.update_or_create(
                                lcode=lcode,
                                defaults={
                                    'name': name,
                                    'district': dist
                                }
                            )
                            l_count += 1
                        except District.DoesNotExist:
                            # This shouldn't happen now if we imported districts first
                            pass

                self.stdout.write(self.style.SUCCESS(f"Imported/Updated {l_count} Locals."))

            conn.close()

        except pymysql.MySQLError as err:
            self.stdout.write(self.style.ERROR(f"MariaDB Error: {err}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
