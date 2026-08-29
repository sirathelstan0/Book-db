# app.py - Complete Flask App (No .env issues)

import os
import sys
import requests
import json
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# ============================================
# ⚠️ CRITICAL: Flask ko .env ignore karne ke liye
# ============================================
os.environ['FLASK_SKIP_DOTENV'] = '1'  # .env file ignore
os.environ['FLASK_ENV'] = 'production'  # Production mode

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ============================================
# 🔐 JSONBIN.IO CONFIGURATION
# ============================================
API_KEY = "$2a$10$hzojE/hSPUHPK9xbg5.WueF17nWrHqaYxZ8.pRyi5bITGYI3PQUL2"
BIN_ID = "6a9319d9da38895dfe20bca0"

headers = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

# ============================================
# 📚 DATABASE FUNCTIONS
# ============================================

def read_books():
    """Read all books from jsonbin.io"""
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('record', {})
        return None
    except Exception as e:
        print(f"Read error: {str(e)}")
        return None

def write_books(data):
    """Write books data to jsonbin.io"""
    try:
        response = requests.put(BASE_URL, json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Write error: {str(e)}")
        return False

def get_book_by_id(book_id):
    """Get single book by ID"""
    data = read_books()
    if not data:
        return None
    for book in data.get('books', []):
        if book['id'] == book_id:
            return book
    return None

# ============================================
# 🎨 HTML TEMPLATE
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sir Athelstan - Book Manager</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&display=swap');
        .font-serif-custom { font-family: 'Playfair Display', serif; }
        .transition-all { transition: all 0.3s ease; }
        .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); }
        .book-cover { aspect-ratio: 2/3; object-fit: cover; }
    </style>
</head>
<body class="bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Header -->
        <header class="border-b-2 border-stone-800 pb-4 mb-8">
            <h1 class="text-4xl md:text-5xl font-serif-custom font-light tracking-widest text-stone-900">
                📚 SIR ATHELSTAN
            </h1>
            <p class="text-sm text-gray-600 mt-1">Book Management Dashboard · jsonbin.io Backend</p>
        </header>

        <!-- Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p class="text-3xl font-bold text-stone-800">{{ books.total_books|default(0) }}</p>
                <p class="text-sm text-gray-500 uppercase tracking-wide">Total Books</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p class="text-3xl font-bold text-stone-800">{{ books.books|length if books else 0 }}</p>
                <p class="text-sm text-gray-500 uppercase tracking-wide">Active Books</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p class="text-3xl font-bold text-stone-800">{{ books.author_info.name|default('N/A') }}</p>
                <p class="text-sm text-gray-500 uppercase tracking-wide">Author</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p class="text-3xl font-bold text-stone-800">{{ books.author_info.location|default('N/A') }}</p>
                <p class="text-sm text-gray-500 uppercase tracking-wide">Location</p>
            </div>
        </div>

        <!-- Add Book Form -->
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
            <h2 class="text-2xl font-serif-custom mb-4">➕ Add New Book</h2>
            <form action="/add" method="POST" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input type="text" name="title" placeholder="Book Title" required class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none">
                <input type="text" name="author" placeholder="Author Name" value="Sir Athelstan" class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none">
                <input type="url" name="cover_image" placeholder="Cover Image URL" required class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none">
                <input type="url" name="google_play_link" placeholder="Google Play Link" required class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none">
                <input type="text" name="description" placeholder="Book Description" required class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none col-span-1 md:col-span-2">
                <input type="number" name="published_year" placeholder="Published Year" required class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none">
                <input type="text" name="genre" placeholder="Genre (e.g., Philosophy / Psychology)" required class="p-3 border border-gray-300 rounded focus:border-stone-800 outline-none">
                <button type="submit" class="bg-stone-800 text-white px-6 py-3 rounded hover:bg-stone-600 transition-all font-medium col-span-1 md:col-span-2">
                    Add Book →
                </button>
            </form>
        </div>

        <!-- Books Grid -->
        <h2 class="text-2xl font-serif-custom mb-4">📖 All Books</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {% if books and books.books %}
                {% for book in books.books %}
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover-lift transition-all">
                    <div class="relative">
                        <img src="{{ book.cover_image }}" alt="{{ book.title }}" class="book-cover w-full">
                        <span class="absolute top-2 right-2 bg-stone-800 text-white text-xs px-2 py-1 rounded">#{{ book.id }}</span>
                    </div>
                    <div class="p-4">
                        <h3 class="font-semibold text-sm mb-1 line-clamp-2">{{ book.title }}</h3>
                        <p class="text-xs text-gray-500 mb-2">{{ book.author }}</p>
                        <p class="text-xs text-gray-400 mb-2">{{ book.genre }}</p>
                        <p class="text-xs text-gray-400 mb-3">{{ book.published_year }}</p>
                        <div class="flex gap-2">
                            <a href="/edit/{{ book.id }}" class="flex-1 bg-blue-600 text-white text-xs text-center px-3 py-2 rounded hover:bg-blue-700 transition-all">
                                ✏️ Edit
                            </a>
                            <a href="/delete/{{ book.id }}" onclick="return confirm('Delete this book?')" class="flex-1 bg-red-600 text-white text-xs text-center px-3 py-2 rounded hover:bg-red-700 transition-all">
                                🗑️ Delete
                            </a>
                        </div>
                        <a href="{{ book.google_play_link }}" target="_blank" class="block text-center mt-2 text-xs text-stone-600 hover:text-stone-900 transition-all">
                            📱 View on Google Play →
                        </a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p class="col-span-full text-gray-500 text-center py-12">No books found. Add your first book above!</p>
            {% endif %}
        </div>

        <!-- Footer -->
        <footer class="mt-12 border-t border-gray-200 pt-6 text-sm text-gray-500 text-center">
            <p>© 2026 Sir Athelstan · Powered by jsonbin.io · Flask API</p>
            <p class="mt-1">
                <a href="/api/books" class="hover:text-stone-800 transition-all">📡 API: /api/books</a>
                <span class="mx-2">·</span>
                <a href="/api/book/1" class="hover:text-stone-800 transition-all">📡 API: /api/book/&lt;id&gt;</a>
            </p>
        </footer>
    </div>
</body>
</html>
'''

# ============================================
# 🚀 FLASK ROUTES
# ============================================

@app.route('/')
def index():
    """Home page - Show all books"""
    books = read_books()
    return render_template_string(HTML_TEMPLATE, books=books)

@app.route('/add', methods=['POST'])
def add_book():
    """Add a new book"""
    title = request.form.get('title')
    author = request.form.get('author', 'Sir Athelstan')
    cover_image = request.form.get('cover_image')
    google_play_link = request.form.get('google_play_link')
    description = request.form.get('description')
    published_year = request.form.get('published_year')
    genre = request.form.get('genre')
    
    if not all([title, cover_image, google_play_link, description, published_year, genre]):
        return jsonify({"error": "All fields required"}), 400
    
    try:
        published_year = int(published_year)
    except:
        return jsonify({"error": "Invalid year"}), 400
    
    current_data = read_books()
    if not current_data:
        current_data = {"books": [], "total_books": 0, "author_info": {"name": "Sir Athelstan", "real_name": "Adil Raza", "location": "Siwan, Bihar, India", "genre": "Philosophy / Psychology"}}
    
    max_id = 0
    for book in current_data.get('books', []):
        if book['id'] > max_id:
            max_id = book['id']
    
    new_book = {
        "id": max_id + 1,
        "title": title,
        "author": author,
        "cover_image": cover_image,
        "google_play_link": google_play_link,
        "description": description,
        "published_year": published_year,
        "genre": genre
    }
    
    current_data['books'].append(new_book)
    current_data['total_books'] = len(current_data['books'])
    
    if write_books(current_data):
        return redirect(url_for('index'))
    else:
        return jsonify({"error": "Failed to save"}), 500

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    """Edit a book"""
    if request.method == 'GET':
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Edit Book #{{ book.id }}</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="max-w-2xl mx-auto px-4 py-12">
                    <h1 class="text-3xl font-serif mb-6">✏️ Edit Book #{{ book.id }}</h1>
                    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <form method="POST" class="space-y-4">
                            <input type="text" name="title" value="{{ book.title }}" required class="w-full p-3 border border-gray-300 rounded">
                            <input type="text" name="author" value="{{ book.author }}" required class="w-full p-3 border border-gray-300 rounded">
                            <input type="url" name="cover_image" value="{{ book.cover_image }}" required class="w-full p-3 border border-gray-300 rounded">
                            <input type="url" name="google_play_link" value="{{ book.google_play_link }}" required class="w-full p-3 border border-gray-300 rounded">
                            <input type="text" name="description" value="{{ book.description }}" required class="w-full p-3 border border-gray-300 rounded">
                            <input type="number" name="published_year" value="{{ book.published_year }}" required class="w-full p-3 border border-gray-300 rounded">
                            <input type="text" name="genre" value="{{ book.genre }}" required class="w-full p-3 border border-gray-300 rounded">
                            <div class="flex gap-4">
                                <button type="submit" class="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition-all flex-1">
                                    💾 Save Changes
                                </button>
                                <a href="/" class="bg-gray-600 text-white px-6 py-3 rounded hover:bg-gray-700 transition-all text-center flex-1">
                                    ↩️ Cancel
                                </a>
                            </div>
                        </form>
                    </div>
                </div>
            </body>
            </html>
        ''', book=book)
    
    # POST - Update book
    title = request.form.get('title')
    author = request.form.get('author')
    cover_image = request.form.get('cover_image')
    google_play_link = request.form.get('google_play_link')
    description = request.form.get('description')
    published_year = request.form.get('published_year')
    genre = request.form.get('genre')
    
    if not all([title, author, cover_image, google_play_link, description, published_year, genre]):
        return jsonify({"error": "All fields required"}), 400
    
    current_data = read_books()
    if not current_data:
        return jsonify({"error": "Data not found"}), 404
    
    book_found = False
    for i, book in enumerate(current_data.get('books', [])):
        if book['id'] == book_id:
            current_data['books'][i] = {
                "id": book_id,
                "title": title,
                "author": author,
                "cover_image": cover_image,
                "google_play_link": google_play_link,
                "description": description,
                "published_year": int(published_year),
                "genre": genre
            }
            book_found = True
            break
    
    if not book_found:
        return jsonify({"error": "Book not found"}), 404
    
    if write_books(current_data):
        return redirect(url_for('index'))
    else:
        return jsonify({"error": "Failed to update"}), 500

@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    """Delete a book"""
    current_data = read_books()
    if not current_data:
        return jsonify({"error": "Data not found"}), 404
    
    book_found = False
    for i, book in enumerate(current_data.get('books', [])):
        if book['id'] == book_id:
            del current_data['books'][i]
            book_found = True
            break
    
    if not book_found:
        return jsonify({"error": "Book not found"}), 404
    
    current_data['total_books'] = len(current_data['books'])
    
    if write_books(current_data):
        return redirect(url_for('index'))
    else:
        return jsonify({"error": "Failed to delete"}), 500

# ============================================
# 📡 JSON API ENDPOINTS
# ============================================

@app.route('/api/books', methods=['GET'])
def api_get_books():
    """Get all books (JSON response)"""
    books = read_books()
    if books:
        return jsonify({
            "success": True,
            "data": books,
            "total": books.get('total_books', 0)
        })
    return jsonify({"success": False, "error": "Failed to fetch data"}), 500

@app.route('/api/book/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    """Get single book by ID (JSON response)"""
    book = get_book_by_id(book_id)
    if book:
        return jsonify({
            "success": True,
            "data": book
        })
    return jsonify({"success": False, "error": "Book not found"}), 404

@app.route('/api/add', methods=['POST'])
def api_add_book():
    """Add a new book via API (JSON request)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "JSON data required"}), 400
    
    required_fields = ['title', 'cover_image', 'google_play_link', 'description', 'published_year', 'genre']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing field: {field}"}), 400
    
    try:
        published_year = int(data['published_year'])
    except:
        return jsonify({"success": False, "error": "Invalid year"}), 400
    
    current_data = read_books()
    if not current_data:
        current_data = {"books": [], "total_books": 0, "author_info": {"name": "Sir Athelstan", "real_name": "Adil Raza", "location": "Siwan, Bihar, India", "genre": "Philosophy / Psychology"}}
    
    max_id = 0
    for book in current_data.get('books', []):
        if book['id'] > max_id:
            max_id = book['id']
    
    new_book = {
        "id": max_id + 1,
        "title": data['title'],
        "author": data.get('author', 'Sir Athelstan'),
        "cover_image": data['cover_image'],
        "google_play_link": data['google_play_link'],
        "description": data['description'],
        "published_year": published_year,
        "genre": data['genre']
    }
    
    current_data['books'].append(new_book)
    current_data['total_books'] = len(current_data['books'])
    
    if write_books(current_data):
        return jsonify({
            "success": True,
            "message": "Book added successfully",
            "book": new_book
        })
    return jsonify({"success": False, "error": "Failed to save"}), 500

@app.route('/api/edit/<int:book_id>', methods=['PUT'])
def api_edit_book(book_id):
    """Edit a book via API (JSON request)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "JSON data required"}), 400
    
    current_data = read_books()
    if not current_data:
        return jsonify({"success": False, "error": "Data not found"}), 404
    
    book_found = False
    for i, book in enumerate(current_data.get('books', [])):
        if book['id'] == book_id:
            if 'title' in data:
                current_data['books'][i]['title'] = data['title']
            if 'author' in data:
                current_data['books'][i]['author'] = data['author']
            if 'cover_image' in data:
                current_data['books'][i]['cover_image'] = data['cover_image']
            if 'google_play_link' in data:
                current_data['books'][i]['google_play_link'] = data['google_play_link']
            if 'description' in data:
                current_data['books'][i]['description'] = data['description']
            if 'published_year' in data:
                current_data['books'][i]['published_year'] = int(data['published_year'])
            if 'genre' in data:
                current_data['books'][i]['genre'] = data['genre']
            
            book_found = True
            updated_book = current_data['books'][i]
            break
    
    if not book_found:
        return jsonify({"success": False, "error": "Book not found"}), 404
    
    if write_books(current_data):
        return jsonify({
            "success": True,
            "message": "Book updated successfully",
            "book": updated_book
        })
    return jsonify({"success": False, "error": "Failed to update"}), 500

@app.route('/api/delete/<int:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    """Delete a book via API"""
    current_data = read_books()
    if not current_data:
        return jsonify({"success": False, "error": "Data not found"}), 404
    
    book_found = False
    for i, book in enumerate(current_data.get('books', [])):
        if book['id'] == book_id:
            del current_data['books'][i]
            book_found = True
            break
    
    if not book_found:
        return jsonify({"success": False, "error": "Book not found"}), 404
    
    current_data['total_books'] = len(current_data['books'])
    
    if write_books(current_data):
        return jsonify({
            "success": True,
            "message": f"Book #{book_id} deleted successfully"
        })
    return jsonify({"success": False, "error": "Failed to delete"}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get statistics (JSON response)"""
    books = read_books()
    if not books:
        return jsonify({"success": False, "error": "No data"}), 404
    
    stats = {
        "total_books": len(books.get('books', [])),
        "author": books.get('author_info', {}).get('name', 'Unknown'),
        "location": books.get('author_info', {}).get('location', 'Unknown'),
        "genres": {}
    }
    
    for book in books.get('books', []):
        genre = book.get('genre', 'Unknown')
        stats['genres'][genre] = stats['genres'].get(genre, 0) + 1
    
    return jsonify({"success": True, "data": stats})

# ============================================
# 🚀 RUN APP
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
