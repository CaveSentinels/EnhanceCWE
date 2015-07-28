import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EnhancedCWE.local_settings")
django.setup()


from cwe.models import Keyword, CWE
from cwe.cwe_search import CWEKeywordSearch
CWEKeywordSearchObj = CWEKeywordSearch()

def print_no_newline(string):
    import sys
    sys.stdout.write(string)
    sys.stdout.flush()

existing_cwe_description = CWE.objects.values('description')
existing_cwe_description = [cwe['description'] for cwe in existing_cwe_description]

existing_cwe_name = CWE.objects.values('name')
existing_cwe_name = [cwe['name'] for cwe in existing_cwe_name]


existing_cwe_description = existing_cwe_description + existing_cwe_name


# TODO: remember to consider both the lists

keywords_from_description = []
for description in existing_cwe_description:
    if description:

        try:
            # Remove stop words from the description
            cleaned_description = CWEKeywordSearchObj.remove_stopwords(description)

            # Stem keywords
            stemmed_description = CWEKeywordSearchObj.stem_text(cleaned_description)

            # Add them to the bulk list
            keywords_from_description = keywords_from_description + stemmed_description

        except:
            print "Error !!"


# Remove duplicates
unique_keywords = list(set(keywords_from_description))

# keywords that do not exist in the database
existing_keywords = Keyword.objects.values('name')
existing_keywords = [kw['name'] for kw in existing_keywords]
to_add_db = [kw for kw in unique_keywords if kw not in existing_keywords]

to_add_db_objs = []
for kw in to_add_db:
    to_add_db_objs.append(Keyword(name=kw))

# This completes feeding all unique keywords in the database
Keyword.objects.bulk_create(to_add_db_objs)


print 'All keywords added !!'




# Part to attach keywords to CWE
cwes = CWE.objects.all()
count = 1
for cwe in cwes:
    cwe_keywords = cwe.keywords.values('name')
    cwe_keywords = [kw['name'] for kw in cwe_keywords]

    cwe_description = cwe.description
    cleaned_description = CWEKeywordSearchObj.remove_stopwords(cwe_description)
    stemmed_description = CWEKeywordSearchObj.stem_text(cleaned_description)

    to_add_cwe = [kw for kw in stemmed_description if kw not in cwe_keywords]

    for kw_name in to_add_cwe:
        kw_obj = Keyword.objects.get(name=kw_name)
        cwe.keywords.add(kw_obj)

    print_no_newline(str(count) + ' ')
    count=count+1


print 'Success'

