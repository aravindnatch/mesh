# Mesh
Our submission to Hack@Brown 2021. Try it out at https://meshcv.tech/

# About
As college students looking to apply to internships for the summer, we realized a gap between submitting a resume and having an actual human review them. We wanted to create a website that solves all of the mysteries of an Application Tracking System to help us and others gain valuable information to score our next interview. Mesh analyzes resumes using machine learning and natural language processing to determine which parts of your resume need work. Mesh also compares your resume to existing job openings found on multiple job boards to see which positions you would be fit for without changing a thing.

# How We Built It
Mesh was built using Python, Scikit-Learn, Natural Language Toolkit (NLTK), Spacy, and Flask. A resume, being as customizable as it is, is notoriously difficult to parse from, making information as simple as an individual's name and email hard to reach. We used NLTK and Spacy to determine which words on a resume correspond to user identifying information like an individual's university, phone number, and name. To determine the level of similarity between a specific job listing and the user’s resume, we used scikit-learn’s cosine similarity function. After parsing the user’s resume and converting it to a text file, we simply ran the cosine similarity algorithm on the specific job listing. For each listing, we stored a number corresponding to how similar the job and resume were, and presented the user with the job listings that had the highest similarity.
