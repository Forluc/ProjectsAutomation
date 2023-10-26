# Generated by Django 4.2.6 on 2023-10-26 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teamapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='rank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teamapp.rank'),
        ),
        migrations.AlterField(
            model_name='student',
            name='rank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_ranks', to='teamapp.rank', verbose_name='Уровень ученика'),
        ),
        migrations.AlterField(
            model_name='team',
            name='project_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_managers', to='teamapp.projectmanager', verbose_name='Менеджер'),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Название проекта')),
                ('description', models.TextField(max_length=20, verbose_name='Описание проекта')),
                ('time', models.TimeField(verbose_name='Время для созванивания')),
                ('week', models.IntegerField(verbose_name='Номер недели')),
                ('project_manager', models.ManyToManyField(related_name='project_managers', to='teamapp.projectmanager', verbose_name='Уровень ученика')),
                ('rank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_ranks', to='teamapp.rank', verbose_name='Уровень ученика')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
            },
        ),
        migrations.AddField(
            model_name='team',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teamapp.project'),
        ),
    ]
