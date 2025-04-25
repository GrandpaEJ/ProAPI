// Main JavaScript file for the ProAPI Blog

document.addEventListener('DOMContentLoaded', function() {
    // Admin page functionality
    setupAdminPage();
    
    // New post page functionality
    setupNewPostPage();
});

// API helper function
async function apiRequest(url, method, data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'test-api-key'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    return await response.json();
}

// Setup admin page functionality
function setupAdminPage() {
    // Edit post functionality
    const editButtons = document.querySelectorAll('.edit-post');
    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-form');
    
    if (editButtons.length && editModal && editForm) {
        // Open edit modal
        editButtons.forEach(button => {
            button.addEventListener('click', async function() {
                const postId = this.getAttribute('data-id');
                
                // Get post data
                const response = await apiRequest(`/api/posts/${postId}`, 'GET');
                const post = response.post;
                
                // Fill form
                document.getElementById('edit-id').value = post.id;
                document.getElementById('edit-title').value = post.title;
                document.getElementById('edit-author').value = post.author;
                document.getElementById('edit-tags').value = post.tags.join(', ');
                document.getElementById('edit-content').value = post.content;
                
                // Show modal
                editModal.style.display = 'block';
            });
        });
        
        // Close modal
        editModal.querySelector('.close').addEventListener('click', function() {
            editModal.style.display = 'none';
        });
        
        // Submit edit form
        editForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const postId = document.getElementById('edit-id').value;
            const title = document.getElementById('edit-title').value;
            const author = document.getElementById('edit-author').value;
            const tagsString = document.getElementById('edit-tags').value;
            const content = document.getElementById('edit-content').value;
            
            // Parse tags
            const tags = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
            
            // Update post
            const response = await apiRequest(`/api/admin/posts/${postId}`, 'PUT', {
                title,
                author,
                content,
                tags
            });
            
            // Close modal and reload page
            editModal.style.display = 'none';
            window.location.reload();
        });
    }
    
    // Delete post functionality
    const deleteButtons = document.querySelectorAll('.delete-post');
    const deleteModal = document.getElementById('delete-modal');
    const confirmDeleteButton = document.getElementById('confirm-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete');
    
    if (deleteButtons.length && deleteModal && confirmDeleteButton && cancelDeleteButton) {
        let currentPostId = null;
        
        // Open delete modal
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                currentPostId = this.getAttribute('data-id');
                deleteModal.style.display = 'block';
            });
        });
        
        // Close modal
        deleteModal.querySelector('.close').addEventListener('click', function() {
            deleteModal.style.display = 'none';
        });
        
        // Cancel delete
        cancelDeleteButton.addEventListener('click', function() {
            deleteModal.style.display = 'none';
        });
        
        // Confirm delete
        confirmDeleteButton.addEventListener('click', async function() {
            if (currentPostId) {
                // Delete post
                const response = await apiRequest(`/api/admin/posts/${currentPostId}`, 'DELETE');
                
                // Close modal and reload page
                deleteModal.style.display = 'none';
                window.location.reload();
            }
        });
    }
}

// Setup new post page functionality
function setupNewPostPage() {
    const newPostForm = document.getElementById('new-post-form');
    const resultMessage = document.getElementById('result-message');
    
    if (newPostForm && resultMessage) {
        newPostForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const title = document.getElementById('title').value;
            const author = document.getElementById('author').value;
            const tagsString = document.getElementById('tags').value;
            const content = document.getElementById('content').value;
            
            // Parse tags
            const tags = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
            
            try {
                // Create post
                const response = await apiRequest('/api/admin/posts', 'POST', {
                    title,
                    author,
                    content,
                    tags
                });
                
                // Show success message
                resultMessage.textContent = response.message;
                resultMessage.className = 'success-message';
                
                // Clear form
                newPostForm.reset();
                
                // Redirect to admin page after a delay
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 2000);
            } catch (error) {
                // Show error message
                resultMessage.textContent = 'Error creating post: ' + error.message;
                resultMessage.className = 'error-message';
            }
        });
    }
}
