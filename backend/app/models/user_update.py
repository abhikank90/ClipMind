# Add this to app/models/user.py in the User class:
# 
# search_queries = relationship("SearchQuery", back_populates="user", cascade="all, delete-orphan")
