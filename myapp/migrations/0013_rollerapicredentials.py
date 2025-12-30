

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_alter_membership_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='RollerAPICredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=255)),
                ('client_secret', models.CharField(max_length=255)),
                ('access_token', models.TextField(blank=True, null=True)),
                ('token_created_at', models.DateTimeField(blank=True, null=True)),
                ('product_id', models.IntegerField(help_text='Roller product ID for this location')),
                ('category_name', models.CharField(default='TESTB', help_text='Product category in Roller system', max_length=100)),
                ('max_capacity', models.IntegerField(default=30, help_text='Maximum jumpers allowed at once')),
                ('deposit_percentage', models.IntegerField(default=50, help_text='Deposit percentage required')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roller_credentials', to='myapp.location')),
            ],
            options={
                'verbose_name_plural': 'Roller API Credentials',
                'unique_together': {('location', 'product_id')},
            },
        ),
    ]
