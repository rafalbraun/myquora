
def build_post_hierarchy(posts):
    post_dict = {post.id: post for post in posts}
    
    hierarchy = []
    
    for post in posts:
        post.children = []
        if post.pid == post.id:
            hierarchy.append(post)
        else:
            parent = post_dict.get(post.pid)
            if parent:
                parent.children.append(post)

    return hierarchy

def truncate_text_by_word(text, max_length):
    words = text.split()
    
    if len(words) == 0:
        return ""
    
    truncated = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(truncated) > max_length:
            break
        truncated.append(word)
        current_length += len(word)

    if len(truncated) < len(words):
        return ' '.join(truncated) + "..."
    
    return text
