from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_add_assignment_test_inputs'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[('bug', 'Bug Report'), ('feedback', 'General Feedback'), ('suggestion', 'Suggestion')],
                    default='feedback', max_length=20,
                )),
                ('message', models.TextField()),
                ('page', models.CharField(blank=True, default='', help_text='Page or URL where the issue occurred', max_length=500)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('resolved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='feedback_reports',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-submitted_at']},
        ),
        migrations.CreateModel(
            name='CourseSurveyResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(help_text='Overall course rating 1–5')),
                ('content_clarity', models.PositiveSmallIntegerField(help_text='How well you understood the content 1–5')),
                ('liked_most', models.TextField(blank=True, default='')),
                ('improve', models.TextField(blank=True, default='')),
                ('would_recommend', models.BooleanField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='survey_responses',
                    to='courses.course',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='survey_responses',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-submitted_at'],
                'unique_together': {('user', 'course')},
            },
        ),
    ]
