import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from app.forms import RecipeForm
from app import db
from app.models import Recipe
from flask import jsonify, render_template_string

main_bp = Blueprint('main', __name__)

# Встроенные рецепты
DEFAULT_RECIPES = [
    {
        'id': 0,
        'title': 'Борщ',
        'short_description': 'Традиционный украинский суп из свеклы и капусты.',
        'instructions': '1. Варите мясной бульон.\n2. Добавьте свеклу, капусту, картошку.\n3. Тушите и подавайте со сметаной.',
        'category': 'Славянская',
        'image': 'borscht.png',
        'is_default': True
    },
    {
        'id': -1,
        'title': 'Паста Карбонара',
        'short_description': 'Итальянская классика с беконом и сливочным соусом.',
        'instructions': '1. Обжарьте бекон.\n2. Сварите пасту.\n3. Перемешайте с яйцами, сыром и перцем.',
        'category': 'Итальянская',
        'image': 'carbonara.png',
        'is_default': True
    },
    {
    'id': -3,
    'title': 'Том Ям',
    'short_description': 'Острый тайский суп с креветками и кокосовым молоком.',
    'instructions': '1. Варите бульон с лемонграссом.\n2. Добавьте грибы и креветки.\n3. Влейте кокосовое молоко.',
    'category': 'Тайская',
    'image': 'tom_yam.png',
    'is_default': True
    },
    {
    'id': -4,
    'title': 'Пицца Маргарита',
    'short_description': 'Классическая итальянская пицца с томатами и сыром моцарелла.',
    'instructions': '1. Приготовьте тесто.\n2. Смажьте томатным соусом.\n3. Выложите сыр и запекайте.',
    'category': 'Итальянская',
    'image': 'pizza.png',
    'is_default': True
    },
    {
    'id': -5,
    'title': 'Шурпа',
    'short_description': 'Наваристый суп из баранины с овощами.',
    'instructions': '1. Отварите мясо.\n2. Добавьте картошку, морковь, лук.\n3. Варите до мягкости.',
    'category': 'Узбекская',
    'image': 'shurpa.png',
    'is_default': True
    }

]

# Главная страница
@main_bp.route('/')
def home():
    search = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '').strip()

    query = Recipe.query

    if search:
        query = query.filter(Recipe.title.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)

    user_recipes = query.order_by(Recipe.id.desc()).all()

    #Фильтрация дефолтных вручную
    filtered_defaults = []
    for r in DEFAULT_RECIPES:
        match_title = not search or search in r['title'].lower()
        match_cat = not category or r['category'] == category
        if match_title and match_cat:
            filtered_defaults.append(r)

    recipes = filtered_defaults + user_recipes
    return render_template('home.html', recipes=recipes)

# Добавить рецепт
@main_bp.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'user_id' not in session:
        flash('Please log in to add a recipe.')
        return redirect(url_for('auth.login'))

    form = RecipeForm()
    if form.validate_on_submit():
        filename = 'default.jpg'
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join('app', 'static', 'images', filename)
            form.image.data.save(image_path)

        new_recipe = Recipe(
            title=form.title.data,
            short_description=form.short_description.data,
            instructions=form.instructions.data,
            category=form.category.data,
            image=filename,
            user_id=session['user_id']
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe successfully added!')
        return redirect(url_for('main.home'))

    return render_template('add_recipe.html', form=form)

# Просмотр пользовательского рецепта
@main_bp.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('view_recipe.html', recipe=recipe)

# Просмотр встроенного рецепта
@main_bp.route('/default/<title>')
def default_recipe(title):
    name = title.replace('_', ' ')
    recipe = next((r for r in DEFAULT_RECIPES if r['title'] == name), None)
    if not recipe:
        flash('Recipe not found.')
        return redirect(url_for('main.home'))

    return render_template('view_recipe.html', recipe=recipe)

# Редактирование рецепта
@main_bp.route('/edit-recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if 'user_id' not in session or recipe.user_id != session['user_id']:
        flash('You do not have permission to edit this recipe.')
        return redirect(url_for('main.home'))

    form = RecipeForm(obj=recipe)

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.short_description = form.short_description.data
        recipe.instructions = form.instructions.data
        recipe.category = form.category.data

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join('app', 'static', 'images', filename))
            recipe.image = filename

        db.session.commit()
        flash('The recipe has been updated.')
        return redirect(url_for('auth.profile'))

    return render_template('edit_recipe.html', form=form, recipe=recipe)

# Удаление рецепта
@main_bp.route('/delete-recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if 'user_id' not in session or recipe.user_id != session['user_id']:
        flash('You do not have permission to delete this recipe.')
        return redirect(url_for('main.home'))

    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe removed.')
    return redirect(url_for('auth.profile'))

@main_bp.route('/search')
def live_search():
    search = request.args.get('q', '').strip().lower()
    category = request.args.get('category')

    # SQL
    query = Recipe.query
    if search:
        query = query.filter(Recipe.title.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)

    user_recipes = query.order_by(Recipe.id.desc()).all()

    # Фильтрация встроенных 
    filtered_defaults = []
    for r in DEFAULT_RECIPES:
        match_title = (not search or search in r['title'].lower())
        match_cat = (not category or r['category'] == category)
        if match_title and match_cat:
            filtered_defaults.append(r)

    recipes = filtered_defaults + user_recipes

    # Рендерим карточки
    rendered = render_template('partials/recipe_cards.html', recipes=recipes)
    return jsonify({'html': rendered})