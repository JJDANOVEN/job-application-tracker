from flask import Flask, render_template, request, redirect, url_for, flash
from database import query, execute, get_options
import json

app = Flask(__name__)
app.secret_key = 'change-this-secret-key'

ENTITIES = {
    'companies': {
        'title': 'Companies', 'table': 'companies', 'pk': 'company_id',
        'fields': [
            ('name', 'Company name', 'text', True), ('industry', 'Industry', 'text', False),
            ('website', 'Website', 'text', False), ('location', 'Location', 'text', False),
            ('notes', 'Notes', 'textarea', False)
        ]
    },
    'jobs': {
        'title': 'Jobs', 'table': 'jobs', 'pk': 'job_id',
        'fields': [
            ('company_id', 'Company', 'company_select', True), ('title', 'Job title', 'text', True),
            ('location', 'Location', 'text', False), ('job_type', 'Job type', 'text', False),
            ('salary_min', 'Minimum salary', 'number', False), ('salary_max', 'Maximum salary', 'number', False),
            ('description', 'Description', 'textarea', False), ('required_skills', 'Required skills (comma-separated)', 'text', False)
        ]
    },
    'applications': {
        'title': 'Applications', 'table': 'applications', 'pk': 'application_id',
        'fields': [
            ('job_id', 'Job', 'job_select', True), ('status', 'Status', 'text', True),
            ('date_applied', 'Date applied (YYYY-MM-DD)', 'date', False),
            ('follow_up_date', 'Follow-up date (YYYY-MM-DD)', 'date', False),
            ('notes', 'Notes', 'textarea', False)
        ]
    },
    'contacts': {
        'title': 'Contacts', 'table': 'contacts', 'pk': 'contact_id',
        'fields': [
            ('company_id', 'Company', 'company_select', False), ('name', 'Contact name', 'text', True),
            ('role', 'Role/title', 'text', False), ('email', 'Email', 'email', False),
            ('phone', 'Phone', 'text', False), ('notes', 'Notes', 'textarea', False)
        ]
    }
}


def get_entity(slug):
    if slug not in ENTITIES:
        return None
    return ENTITIES[slug]



def build_form_data(entity, form):
    data = {}
    for field, label, kind, required in entity['fields']:
        value = form.get(field, '').strip()
        if required and not value:
            raise ValueError(f'{label} is required.')
        if value == '':
            data[field] = None
        elif kind == 'number':
            data[field] = float(value)
        elif kind in ('company_select', 'job_select'):
            data[field] = int(value)
        else:
            data[field] = value
    return data


@app.route('/')
def index():
    summary = {
        'companies': query('SELECT COUNT(*) AS total FROM companies')[0]['total'],
        'jobs': query('SELECT COUNT(*) AS total FROM jobs')[0]['total'],
        'applications': query('SELECT COUNT(*) AS total FROM applications')[0]['total'],
        'contacts': query('SELECT COUNT(*) AS total FROM contacts')[0]['total']
    }
    recent = query('''SELECT a.application_id, j.title AS job_title, c.name AS company_name,
                     a.status, a.date_applied FROM applications a
                     JOIN jobs j ON a.job_id=j.job_id JOIN companies c ON j.company_id=c.company_id
                     ORDER BY a.application_id DESC LIMIT 5''')
    return render_template('index.html', summary=summary, recent=recent)


@app.route('/<slug>')
def list_entity(slug):
    entity = get_entity(slug)
    if not entity:
        return 'Page not found', 404
    if slug == 'companies':
        rows = query('SELECT * FROM companies ORDER BY company_id DESC')
    elif slug == 'jobs':
        rows = query('SELECT j.*, c.name AS company_name FROM jobs j JOIN companies c ON j.company_id=c.company_id ORDER BY j.job_id DESC')
    elif slug == 'applications':
        rows = query('''SELECT a.*, j.title AS job_title, c.name AS company_name FROM applications a
                     JOIN jobs j ON a.job_id=j.job_id JOIN companies c ON j.company_id=c.company_id
                     ORDER BY a.application_id DESC''')
    else:
        rows = query('''SELECT ct.*, c.name AS company_name FROM contacts ct
                     LEFT JOIN companies c ON ct.company_id=c.company_id ORDER BY ct.contact_id DESC''')
    options = get_options()
    return render_template('entity.html', slug=slug, entity=entity, rows=rows, options=options, edit_row=None)


@app.route('/<slug>/add', methods=['POST'])
def add_entity(slug):
    entity = get_entity(slug)
    if not entity:
        return 'Page not found', 404
    try:
        data = build_form_data(entity, request.form)
        cols = list(data.keys())
        sql = f"INSERT INTO {entity['table']} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})"
        execute(sql, tuple(data[c] for c in cols))
        flash(f"{entity['title'][:-1] if entity['title'].endswith('s') else entity['title']} added.", 'success')
    except Exception as error:
        flash(f'Could not save: {error}', 'error')
    return redirect(url_for('list_entity', slug=slug))


@app.route('/<slug>/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_entity(slug, item_id):
    entity = get_entity(slug)
    if not entity:
        return 'Page not found', 404
    if request.method == 'POST':
        try:
            data = build_form_data(entity, request.form)
            cols = list(data.keys())
            sql = f"UPDATE {entity['table']} SET " + ', '.join(f'{c}=%s' for c in cols) + f" WHERE {entity['pk']}=%s"
            execute(sql, tuple(data[c] for c in cols) + (item_id,))
            flash('Record updated.', 'success')
            return redirect(url_for('list_entity', slug=slug))
        except Exception as error:
            flash(f'Could not update: {error}', 'error')
    item = query(f"SELECT * FROM {entity['table']} WHERE {entity['pk']}=%s", (item_id,))
    if not item:
        return 'Record not found', 404
    rows = query(f"SELECT * FROM {entity['table']} ORDER BY {entity['pk']} DESC")
    return render_template('entity.html', slug=slug, entity=entity, rows=rows, options=get_options(), edit_row=item[0])


@app.route('/<slug>/delete/<int:item_id>', methods=['POST'])
def delete_entity(slug, item_id):
    entity = get_entity(slug)
    if not entity:
        return 'Page not found', 404
    try:
        execute(f"DELETE FROM {entity['table']} WHERE {entity['pk']}=%s", (item_id,))
        flash('Record deleted.', 'success')
    except Exception as error:
        flash(f'Could not delete. It may be linked to another record: {error}', 'error')
    return redirect(url_for('list_entity', slug=slug))


@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    skills_text = request.form.get('skills', '') if request.method == 'POST' else ''
    jobs = query('SELECT j.*, c.name AS company_name FROM jobs j JOIN companies c ON j.company_id=c.company_id ORDER BY j.job_id DESC')
    user_skills = {s.strip().lower() for s in skills_text.split(',') if s.strip()}
    results = []
    if request.method == 'POST':
        for job in jobs:
            required = {s.strip().lower() for s in (job.get('required_skills') or '').split(',') if s.strip()}
            matched = required & user_skills
            percent = round((len(matched) / len(required)) * 100) if required else 0
            results.append({'job': job, 'percent': percent, 'matched': sorted(matched), 'missing': sorted(required - matched)})
        results.sort(key=lambda x: x['percent'], reverse=True)
    return render_template('match.html', skills_text=skills_text, results=results)


if __name__ == '__main__':
    app.run(debug=True)
