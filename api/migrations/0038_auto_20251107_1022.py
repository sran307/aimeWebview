from django.db import migrations

def add_initial_mf_names(apps, schema_editor):
    MfNames = apps.get_model('api', 'mfNames')  # <-- use your app name here ('api')

    # List of default Mutual Fund names to insert
    default_mfs = [
        "Axis Bluechip Fund",
        "HDFC Balanced Advantage Fund",
        "ICICI Prudential Equity & Debt Fund",
        "SBI Small Cap Fund",
        "Nippon India Growth Fund",
    ]

    for name in default_mfs:
        MfNames.objects.get_or_create(mfName=name)

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_mfnames'),
    ]

    operations = [
        migrations.RunPython(add_initial_mf_names),
    ]
