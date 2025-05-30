# Generated by Django 5.1.3 on 2025-03-18 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("PassManagement", "0003_c_d_e_f_g_h_i_j_k_l_lowercase_a_lowercase_b_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="a",
            name="first_character",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name="a",
            name="fourth_character",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name="a",
            name="second_character",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name="a",
            name="third_character",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddIndex(
            model_name="a",
            index=models.Index(
                fields=["first_character", "second_character"],
                name="PassManagem_first_c_317056_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="a",
            index=models.Index(
                fields=["third_character", "fourth_character"],
                name="PassManagem_third_c_aefa3f_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="a",
            index=models.Index(fields=["hash"], name="PassManagem_hash_235f16_idx"),
        ),
    ]
