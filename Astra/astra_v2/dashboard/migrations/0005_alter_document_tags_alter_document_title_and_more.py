# Generated by Django 5.0.6 on 2024-05-15 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_document_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(to='dashboard.tag'),
        ),
        migrations.AlterField(
            model_name='document',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='document',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
