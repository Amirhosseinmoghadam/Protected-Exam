# models.py
from datetime import datetime

import pandas
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from random import randint

from accounts.models import CustomUser


class Exam(models.Model):
    """Store the details needed to identify each exam.

    Fields:
        title (str): The title of the exam.
        total_questions (int): The number of questions in each exam.
        file_row_len (int): The count of questions in each exam file.
        question_file (str): The address of the questions file.
        start (datetime.datetime): The start date and hour of the exam.
        end (datetime.datetime): The end date and hour of the exam.
    """
    title = models.CharField(max_length=50)
    total_questions = models.IntegerField(default=20)
    file_row_len = models.IntegerField(default=200)
    question_file = models.FileField(upload_to='exam/', null=True, blank=True)
    is_face_scan_needed = models.BooleanField(default=False)
    is_voice_record_needed = models.BooleanField(default=False)
    exam_time = models.TimeField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    def assign_random_questions(self):
        """Give a random number of questions to the user,
        start from a random field and go to the next *total_questions
        of the questions. return the questions"""

        exam_questions = pandas.read_excel(self.question_file)
        used_questions = []
        exam_file = []
        i = 0
        #Generate a random index and get the question from it
        while i < self.total_questions:
            k = randint(1, self.file_row_len - 1)
            if k in used_questions:
                i -= 1
            else:
                exam_file.append(exam_questions.iloc[k])
                used_questions.append(k)
                i += 1

        return exam_file


    def __str__(self):
        return self.title


class Answer(models.Model):
    """Make the model to detect the state of the user's answers.
    Fields:
    exam: The uuid of the associated exam
    user: The uuid of the associated user
    score: The number of correct answers
    start_time: datetime the exam begun
    submit_time: datetime the exam was submitted
    answer: a JSON field containing all the answers the user gave to
    each question with the id of each question, and it's given answer.

    Example:
     exam: <Exam: bigExam>,
    user: <User: admin>,
    score: 4,
    start_time: '2011-11-04T00:05:23+04:30',
    submit_time: '2011-11-04T00:15:23+04:30',
    answer: {
        1: "a",
        2: "b",
        ...
    }
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    submit_time = models.DateTimeField(null=True, blank=True)
    answer = models.JSONField(default=dict)


    def save(self, *args, **kwargs):
        try:
            self.validate_answer_format()
            self.score = self.calculate_score()
            super().save(*args, **kwargs)
        except ValidationError as e:
            raise e


    def validate_answer_format(self, answer_ = None):
        """Receive the answers user gave and make sure tht they are
        formatted correctly"""
        if not answer_:
            answer_ = self.answer
        exam = self.exam
        count = exam.total_questions
        if not isinstance(answer_, dict):
            raise ValidationError("Answers must be a dictionary.")

        if len(answer_) != count:
            raise ValidationError(f"There must be exactly {count}"
                                  f" items in the answers.")

        # Validate each key-value pair
        for key, val in answer_.items():
            key = int(key)
            # Ensure the key is an integer
            if not isinstance(key, int):
                raise ValidationError(f"Key {key} must be an integer")

            # Ensure the value is in defined format
            if val not in ['a', 'b', 'c', 'd', '']:
                raise ValidationError(f"Value for key {key} must be one"
                                      f" of 'a', 'b', 'c', 'd', or ''.")


    def calculate_score(self):
        """Check the answers that our user has given and score them from 0"""
        score = 0
        exam = self.exam
        exam_file = pandas.read_excel(exam.question_file)
        for key, value in self.answer.items():
            key = int(key)
            print(exam_file["correct"][key-1])
            if value == exam_file["correct"][key-1]:
                score += 1
        return score
