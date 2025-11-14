from django.db import migrations

def add_initial_mf_names(apps, schema_editor):
    MfNames = apps.get_model('api', 'mfNames')  # <-- use your app name here ('api')

    # List of default Mutual Fund names to insert
    default_mfs = [
        "Canara Robeco Small Cap Fund",
        "Parag Parikh Flexi Cap Fund",
        "HDFC Midcap Fund",
        "Edelweiss Gold & Silver ETF",
        "Franklin US Equity",
        "ICICI Prudential Divident Fund",
        "ICICI Prudential Savings Fund",
        "BitCoin",
        "Ethereum"
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
