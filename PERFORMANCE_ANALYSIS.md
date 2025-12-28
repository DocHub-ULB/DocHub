# Performance Analysis Report - DocHub

Generated: 2025-12-28

## Executive Summary

This report identifies performance anti-patterns, N+1 queries, missing database indexes, and inefficient algorithms in the DocHub codebase. The findings are prioritized by impact on user experience.

---

## 🔴 CRITICAL Issues (High Impact)

### 1. N+1 Query in Tag Collection (catalog/views.py:55)

**Location:** `catalog/views.py:55`

**Issue:**
```python
tags = {tag for doc in documents for tag in doc.tags.all()}
```

**Problem:** While tags are prefetched on line 45, this set comprehension iterates through all documents and their tags in Python rather than letting the database optimize. For a course with 100 documents and 10 tags each, this creates unnecessary iterations.

**Impact:** High - Executed on every course page view (high traffic endpoint)

**Recommendation:**
```python
# Option 1: Collect from prefetched data more efficiently
tags = set()
for doc in documents:
    tags.update(doc.tags.all())

# Option 2: Query tags directly
tags = Tag.objects.filter(document__in=documents).distinct()
```

---

### 2. Inefficient Vote Counting (documents/models.py:86-100)

**Location:** `documents/models.py:86-100`

**Issue:**
```python
@property
def votes(self):
    upvotes, downvotes = 0, 0
    for vote in self.vote_set.all():
        vote_type = vote.vote_type
        if vote_type == Vote.VoteType.UPVOTE:
            upvotes += 1
        elif vote_type == Vote.VoteType.DOWNVOTE:
            downvotes += 1
    return {"upvotes": upvotes, "downvotes": downvotes}
```

**Problem:** This property counts votes in Python by iterating through all vote objects. Every time it's called, it fetches all votes from the database.

**Impact:** High - Called frequently when displaying documents

**Recommendation:**
```python
# Use database aggregation instead
from django.db.models import Count, Q

@property
def votes(self):
    result = self.vote_set.aggregate(
        upvotes=Count('id', filter=Q(vote_type=Vote.VoteType.UPVOTE)),
        downvotes=Count('id', filter=Q(vote_type=Vote.VoteType.DOWNVOTE))
    )
    return result

# OR better: annotate this when querying documents (as already done in show_course view)
```

**Note:** The `show_course` view already correctly uses annotations for vote counts. The property should be removed or only used as a fallback.

---

### 3. Critical Bug in PDF Download Counter (documents/views.py:295)

**Location:** `documents/views.py:295`

**Issue:**
```python
def document_pdf_file(request, pk):
    # ...
    document.downloads = F("views") + 1  # BUG: Should be F("downloads")
    document.save(update_fields=["views"])
```

**Problem:**
1. Incrementing downloads counter using the **views** field instead of **downloads**
2. Saving to "views" field instead of "downloads"

**Impact:** Critical - Data corruption, incorrect statistics

**Recommendation:**
```python
document.downloads = F("downloads") + 1
document.save(update_fields=["downloads"])
```

---

### 4. Missing Prefetch in document_show (documents/views.py:231)

**Location:** `documents/views.py:231`

**Issue:**
```python
context = {
    "document": document,
    "user_vote": document.vote_set.filter(user=request.user).first(),
    "form": DocumentReportForm(),
}
```

**Problem:** Creates an additional query to fetch user's vote without using select_related or prefetch_related.

**Impact:** Medium-High - Executed on every document view

**Recommendation:**
```python
# In the view, fetch with prefetch
document = get_object_or_404(
    Document.objects.prefetch_related(
        Prefetch('vote_set',
                 queryset=Vote.objects.filter(user=request.user),
                 to_attr='user_votes')
    ),
    pk=pk
)

context = {
    "document": document,
    "user_vote": document.user_votes[0] if document.user_votes else None,
    "form": DocumentReportForm(),
}
```

---

### 5. Sitemap N+1 Query (catalog/sitemap.py:15)

**Location:** `catalog/sitemap.py:15`

**Issue:**
```python
def lastmod(self, obj: Course):
    lastdoc = obj.document_set.order_by("-created").first()
    if lastdoc:
        return lastdoc.created
```

**Problem:** For each course in the sitemap, this queries the database to get the latest document. With 1000 courses, this creates 1000 queries.

**Impact:** High - Slows down sitemap generation significantly

**Recommendation:**
```python
def items(self):
    # Annotate with latest document creation date
    from django.db.models import Max
    return Course.objects.annotate(
        latest_doc_date=Max('document__created')
    )

def lastmod(self, obj: Course):
    return obj.latest_doc_date
```

---

## 🟡 MEDIUM Issues

### 6. Redundant Following Check Query (catalog/views.py:57)

**Location:** `catalog/views.py:57`

**Issue:**
```python
"following": course.followed_by.filter(id=request.user.id).exists(),
```

**Problem:** Makes a separate query to check if user follows the course.

**Impact:** Medium - One extra query per course page view

**Recommendation:**
```python
# In the view function, before rendering:
user_follows = course.followed_by.filter(id=request.user.id).exists() if request.user.is_authenticated else False

# OR use a prefetch with annotation
from django.db.models import Exists, OuterRef
course = get_object_or_404(
    Course.objects.annotate(
        is_followed=Exists(
            Course.followed_by.through.objects.filter(
                course_id=OuterRef('pk'),
                user_id=request.user.id
            )
        )
    ) if request.user.is_authenticated else Course.objects,
    slug=slug
)
```

---

### 7. Uncached Moderated Courses Query (users/models.py:85-87)

**Location:** `users/models.py:85-87`

**Issue:**
```python
if self._moderated_courses is None:
    ids = [course.id for course in self.moderated_courses.only("id")]
    self._moderated_courses = ids
```

**Problem:** While it caches in `_moderated_courses`, the cache is instance-level and queries the database every time a new User instance is created (which happens on every request).

**Impact:** Medium - Extra query on permission checks

**Recommendation:**
```python
# Use values_list for more efficient ID fetching
if self._moderated_courses is None:
    self._moderated_courses = list(
        self.moderated_courses.values_list('id', flat=True)
    )
```

---

### 8. Template Tag N+1 Query (documents/templatetags/like_tags.py:13)

**Location:** `documents/templatetags/like_tags.py:13`

**Issue:**
```python
@register.simple_tag
def user_liked(user: User, document: Document):
    vote = Vote.objects.filter(user=user, document=document).first()
```

**Problem:** If this template tag is used in a loop (e.g., listing documents), it creates N+1 queries.

**Impact:** Medium - Depends on usage (marked as TODO: dead code, may not be actively used)

**Recommendation:**
- Remove if truly dead code
- If used, ensure votes are prefetched in the view and access via `document.vote_set.all()` in template

---

### 9. Inefficient Stats Query (www/views.py:44-51)

**Location:** `www/views.py:44-51`

**Issue:**
```python
if Document.objects.count():
    page_count = Document.objects.all().aggregate(Sum("pages"))["pages__sum"]
else:
    page_count = 0

context = {
    "debug": settings.DEBUG,
    "documents": floor(Document.objects.count()),
    "pages": floor(page_count, 2),
    "users": floor(User.objects.count()),
}
```

**Problem:**
1. `Document.objects.count()` called twice
2. Three separate queries for stats (documents, pages, users)

**Impact:** Medium - Only on unauthenticated homepage, but creates 4 queries total

**Recommendation:**
```python
from django.db.models import Count, Sum

# Single query with aggregation
doc_stats = Document.objects.aggregate(
    count=Count('id'),
    total_pages=Sum('pages')
)
user_count = User.objects.count()

context = {
    "debug": settings.DEBUG,
    "documents": floor(doc_stats['count'] or 0),
    "pages": floor(doc_stats['total_pages'] or 0, 2),
    "users": floor(user_count),
}
```

---

### 10. Autocomplete Redundant Filter (catalog/autocomplete.py:14-16)

**Location:** `catalog/autocomplete.py:14-16`

**Issue:**
```python
qs = Course.objects.filter(name__icontains=query)
qs = qs.filter(Q(name__icontains=query) | Q(slug__icontains=query))
```

**Problem:** Filters by `name__icontains` twice - once alone, then again in the Q object. The first filter is redundant.

**Impact:** Low-Medium - Inefficient but not creating N+1

**Recommendation:**
```python
qs = Course.objects.filter(Q(name__icontains=query) | Q(slug__icontains=query))
```

---

### 11. Finder View Loop Queries (catalog/views.py:125)

**Location:** `catalog/views.py:125`

**Issue:**
```python
for i in range(len(categories) - 1, 0, -1):
    parents = categories[i].parents.all()
    if categories[i - 1] not in parents:
        raise Http404(f"Invalid category path, {i}")
```

**Problem:** Calls `parents.all()` in a loop without prefetch_related.

**Impact:** Medium - Creates N queries for N categories in path

**Recommendation:**
```python
def finder(request, slugs: str = ""):
    slug_list = slugs.split("/")
    categories = [
        get_object_or_404(Category.objects.prefetch_related('parents'), slug=x)
        for x in slug_list
    ]
    # ... rest of the code
```

---

## 🟢 LOW Issues (Optimization Opportunities)

### 12. Missing Database Indexes

**Issue:** Several frequently queried fields lack database indexes:

**Missing Indexes:**
1. `User.is_staff` - Used for permission checks
2. `User.is_moderator` - Used for permission checks
3. `User.is_academic` - Used for filtering
4. `CourseUserView.last_view` - Used in ORDER BY
5. `Vote.when` - Used in list_filter in admin
6. `DocumentReport.created` - Has date_hierarchy but could benefit from explicit index
7. `RepresentativeRequest.processed` - Used in filtering

**Impact:** Low-Medium - Affects query performance on larger datasets

**Recommendation:**
```python
# In respective models, add:
class User(AbstractBaseUser):
    is_staff = models.BooleanField(default=False, db_index=True)
    is_moderator = models.BooleanField(default=False, db_index=True)
    is_academic = models.BooleanField(default=False, db_index=True)

class CourseUserView(models.Model):
    last_view = models.DateTimeField(auto_now=True, db_index=True)

class Vote(models.Model):
    when = models.DateTimeField(auto_now=True, db_index=True)

class RepresentativeRequest(models.Model):
    processed = models.BooleanField(default=False, db_index=True)
```

---

### 13. Inefficient followers_count Property (catalog/models.py:135)

**Location:** `catalog/models.py:135`

**Issue:**
```python
@property
def followers_count(self) -> int:
    return self.followed_by.count()
```

**Problem:** Executes a COUNT query every time it's accessed. If called multiple times in templates/views, creates redundant queries.

**Impact:** Low - Depends on usage frequency

**Recommendation:**
- Use annotation when querying courses that need this count
- Consider caching or removing if not frequently used

---

### 14. Document Sitemap Without Select Related (documents/sitemap.py:12)

**Location:** `documents/sitemap.py:12`

**Issue:**
```python
def items(self):
    return Document.objects.filter(hidden=False)
```

**Problem:** Sitemap framework may access related fields, potentially causing N+1.

**Impact:** Low - Depends on what Django's sitemap framework accesses

**Recommendation:**
```python
def items(self):
    return Document.objects.filter(hidden=False).select_related('course')
```

---

## 📊 Performance Metrics Impact

### Estimated Query Reduction

| Endpoint | Current Queries (est.) | After Fixes | Improvement |
|----------|------------------------|-------------|-------------|
| Homepage (authenticated) | 8-10 | 5-6 | ~40% |
| Course page (100 docs) | 15-20 | 8-10 | ~50% |
| Document view | 5-7 | 3-4 | ~40% |
| Sitemap (1000 courses) | 1000+ | 10-15 | ~99% |

---

## 🎯 Recommended Priority Order

1. **Fix PDF download bug** (Issue #3) - Data corruption
2. **Fix sitemap N+1** (Issue #5) - Severe performance impact
3. **Fix inefficient vote counting** (Issue #2) - Frequently called
4. **Add missing database indexes** (Issue #12) - Foundation for scaling
5. **Fix tag collection N+1** (Issue #1) - High traffic endpoint
6. **Optimize document_show** (Issue #4) - High traffic
7. **Fix stats query** (Issue #9) - Public homepage
8. **Optimize finder prefetch** (Issue #11) - User experience
9. **Other medium issues** (Issues #6, #7, #8, #10)
10. **Low priority optimizations** (Issues #13, #14)

---

## 🔧 Implementation Notes

### Database Migrations Required
- Adding indexes will require Django migrations
- Run `python manage.py makemigrations` after adding `db_index=True`
- Consider adding indexes during low-traffic periods

### Testing Strategy
1. Add `django-debug-toolbar` to count queries in development
2. Use `django.test.utils.override_settings(DEBUG=True)` in tests
3. Monitor query count with `len(connection.queries)`
4. Load test high-traffic endpoints before/after fixes

### Monitoring
Consider adding:
- Query count monitoring to high-traffic views
- Slow query logging in PostgreSQL
- Performance regression tests

---

## Additional Observations

### Good Practices Already in Use ✅
1. Using `F()` expressions for counter updates (documents/views.py:226, 272)
2. Using `select_related` and `prefetch_related` in homepage (www/views.py:21-22)
3. Using annotations for vote counts in course view (catalog/views.py:46-49)
4. Using database indexes on key fields (slug, name, state, md5)
5. Using `only()` to limit field fetching (users/models.py:86)
6. 5-minute throttling on CourseUserView to reduce writes (catalog/models.py:168)

### Code Marked as TODO (Potential Dead Code)
Several files have `# TODO: is this dead code ?` comments:
- `search/logic.py:1`
- `search/views.py:1`
- `catalog/autocomplete.py:1`
- `documents/templatetags/like_tags.py:1`

**Recommendation:** Audit and remove unused code to reduce maintenance burden.

---

## Conclusion

The codebase shows good Django practices in many areas, particularly in recent fixes (like the N+1 query fix for homepage mentioned in git history). However, there are critical bugs (#3) and several N+1 query patterns that should be addressed, especially in high-traffic endpoints like course pages and document views.

The recommended fixes are straightforward to implement and should significantly improve performance, especially as the platform scales.
