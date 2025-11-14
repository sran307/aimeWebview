from django.db import migrations

def add_initial_stockheadings(apps, schema_editor):
    # Get the model dynamically (no direct import allowed here)
    StockHeadings = apps.get_model('assets', 'stockHeadings')

    # ✅ Add your data here
    data = [
        'stockName',
        'transaction',
        'quantity',
        'amntPerStock',
        'brockerage',
        'buyReason',
        'sellReason',
        'remarks',
        'transDate'
    ]

    # Insert each record
    for item in data:
        StockHeadings.objects.create(itemName=item)


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),  # this ensures table is created first
    ]

    operations = [
        migrations.RunPython(add_initial_stockheadings),
    ]
