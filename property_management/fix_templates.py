import os

# Define the cleaned content for building_list.html
building_list_content = r'''{% extends 'properties/base.html' %}

{% block title %}Buildings (Gusali) - Property Management{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <h2><i class="fas fa-building me-2"></i>Buildings (Gusali)</h2>
                <div>
                    <a href="{% url 'gusali:building_report' %}" class="btn btn-outline-info me-2">
                        <i class="fas fa-chart-bar me-1"></i>Report
                    </a>
                    <a href="{% url 'gusali:building_upload' %}" class="btn btn-primary">
                        <i class="fas fa-upload me-2"></i>Upload Report
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Search Box -->
    <div class="row mb-3">
        <div class="col-12">
            <div class="card">
                <div class="card-body py-3">
                    <form method="get" class="row g-2 align-items-center">
                        <div class="col-md-6">
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-search"></i></span>
                                <input type="text" name="q" class="form-control"
                                    placeholder="Search by District Code, District Name, Local Code, or Local Name..."
                                    value="{{ search_query }}">
                                <button type="submit" class="btn btn-primary">Search</button>
                            </div>
                        </div>
                        <div class="col-md-6 text-end">
                            <small class="text-muted">
                                <i class="fas fa-info-circle"></i>
                                Search: dcode, distrito, lcode, lokal, building name
                            </small>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header py-2">
                    <h6 class="mb-0"><i class="fas fa-filter me-2"></i>Filter Buildings</h6>
                </div>
                <div class="card-body">
                    <form method="get" class="row g-3">
                        <!-- Keep search query -->
                        {% if search_query %}
                        <input type="hidden" name="q" value="{{ search_query }}">
                        {% endif %}

                        <!-- District Filter -->
                        <div class="col-md-3">
                            <label class="form-label">District (Distrito)</label>
                            <select name="district" class="form-select">
                                <option value="">All Districts</option>
                                {% for district in districts %}
                                <option value="{{ district.dcode }}" {% if current_district == district.dcode %}selected{% endif %}>
                                    {{ district.name }} ({{ district.dcode }})
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <!-- Local Filter -->
                        <div class="col-md-3">
                            <label class="form-label">Local (Lokal)</label>
                            <select name="local" class="form-select">
                                <option value="">All Locals</option>
                                {% for local in locals %}
                                <option value="{{ local.lcode }}" {% if current_local == local.lcode %}selected{% endif %}>
                                    {{ local.name }} ({{ local.lcode }})
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <!-- Building Code Filter -->
                        <div class="col-md-2">
                            <label class="form-label">Building Code</label>
                            <select name="code" class="form-select">
                                <option value="">All Codes</option>
                                {% for code, label in code_choices %}
                                <option value="{{ code }}" {% if current_code == code %}selected{% endif %}>
                                    {{ label }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <!-- Year Filter -->
                        <div class="col-md-2">
                            <label class="form-label">Year</label>
                            <select name="year" class="form-select">
                                <option value="">All Years</option>
                                {% for year in years %}
                                <option value="{{ year }}" {% if current_year == year|stringformat:"s" %}selected{% endif %}>
                                    {{ year }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <!-- Filter Buttons -->
                        <div class="col-md-2 d-flex align-items-end">
                            <button type="submit" class="btn btn-outline-primary me-2">
                                <i class="fas fa-filter me-1"></i>Filter
                            </button>
                            <a href="{% url 'gusali:building_list' %}" class="btn btn-outline-secondary">
                                <i class="fas fa-times"></i>
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Summary Card -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title mb-0">Total Buildings</h6>
                            <h2 class="mb-0">{{ buildings.count }}</h2>
                        </div>
                        <i class="fas fa-building fa-2x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title mb-0">Total Cost</h6>
                            <h2 class="mb-0">₱{{ total_cost|floatformat:2|default:"0.00" }}</h2>
                        </div>
                        <i class="fas fa-peso-sign fa-2x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Active Filters Display -->
    {% if search_query or current_district or current_local or current_code or current_year %}
    <div class="row mb-3">
        <div class="col-12">
            <div class="d-flex flex-wrap gap-2 align-items-center">
                <span class="text-muted">Active Filters:</span>
                {% if search_query %}
                <span class="badge bg-info">Search: {{ search_query }}</span>
                {% endif %}
                {% if current_district %}
                <span class="badge bg-secondary">District: {{ current_district }}</span>
                {% endif %}
                {% if current_local %}
                <span class="badge bg-secondary">Local: {{ current_local }}</span>
                {% endif %}
                {% if current_code %}
                <span class="badge bg-primary">Code: {{ current_code }}</span>
                {% endif %}
                {% if current_year %}
                <span class="badge bg-warning text-dark">Year: {{ current_year }}</span>
                {% endif %}
                <a href="{% url 'gusali:building_list' %}" class="btn btn-sm btn-outline-danger">
                    <i class="fas fa-times me-1"></i>Clear All
                </a>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Buildings Table -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Building List</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>Code</th>
                                    <th>Building Name</th>
                                    <th>Classification</th>
                                    <th>Local</th>
                                    <th>District</th>
                                    <th>Capacity</th>
                                    <th>Status</th>
                                    <th class="text-end">Current Cost</th>
                                    <th>Year</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for building in buildings %}
                                <tr>
                                    <td><span class="badge bg-primary">{{ building.code }}</span></td>
                                    <td>{{ building.name }}</td>
                                    <td>{{ building.classification|default:"-" }}</td>
                                    <td>
                                        {% if building.local %}
                                        <small class="text-muted">{{ building.local.lcode }}</small>
                                        {{ building.local.name }}
                                        {% else %}
                                        <span class="text-muted">-</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if building.local and building.local.district %}
                                        <small class="text-muted">{{ building.local.district.dcode }}</small>
                                        {{ building.local.district.name }}
                                        {% else %}
                                        <span class="text-muted">-</span>
                                        {% endif %}
                                    </td>
                                    <td>{{ building.capacity|default:"-" }}</td>
                                    <td>
                                        {% if building.is_donated %}
                                        <span class="badge bg-success">HANDOG</span>
                                        {% else %}
                                        <span class="badge bg-secondary">-</span>
                                        {% endif %}
                                    </td>
                                    <td class="text-end">₱{{ building.current_total_cost|floatformat:2 }}</td>
                                    <td>{{ building.year_covered }}</td>
                                    <td>
                                        <a href="{% url 'gusali:building_detail' building.pk %}"
                                            class="btn btn-sm btn-outline-primary" title="View Details">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                    </td>
                                </tr>
                                {% empty %}
                                <tr>
                                    <td colspan="10" class="text-center text-muted py-4">
                                        <i class="fas fa-building fa-3x mb-3 d-block"></i>
                                        {% if search_query or current_district or current_local %}
                                        No buildings found matching your search criteria.
                                        <br><a href="{% url 'gusali:building_list' %}">Clear filters</a>
                                        {% else %}
                                        No buildings found. <a href="{% url 'gusali:building_upload' %}">Upload a GUSALI
                                            report</a> to get started.
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Define the cleaned content for item_list.html
item_list_content = r'''{% extends 'properties/base.html' %}

{% block title %}Kagamitan Items - Property Management{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <h2><i class="fas fa-boxes me-2"></i>Kagamitan Items</h2>
                <div>
                    <a href="{% url 'kagamitan:item_report' %}" class="btn btn-outline-info me-2">
                        <i class="fas fa-chart-bar me-1"></i>Report
                    </a>
                    <a href="{% url 'kagamitan:item_upload' %}" class="btn btn-primary">
                        <i class="fas fa-upload me-2"></i>Upload Report
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Search Box -->
    <div class="row mb-3">
        <div class="col-12">
            <div class="card">
                <div class="card-body py-3">
                    <form method="get" class="row g-2 align-items-center">
                        <div class="col-md-6">
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-search"></i></span>
                                <input type="text" name="q" class="form-control"
                                    placeholder="Search by Item Name, Prop No, Brand, District, or Local..."
                                    value="{{ search_query }}">
                                <button type="submit" class="btn btn-primary">Search</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header py-2">
                    <h6 class="mb-0"><i class="fas fa-filter me-2"></i>Filter Items</h6>
                </div>
                <div class="card-body">
                    <form method="get" class="row g-3">
                        {% if search_query %}
                        <input type="hidden" name="q" value="{{ search_query }}">
                        {% endif %}

                        <div class="col-md-3">
                            <label class="form-label">District</label>
                            <select name="district" class="form-select">
                                <option value="">All Districts</option>
                                {% for district in districts %}
                                <option value="{{ district.dcode }}" {% if current_district == district.dcode %}selected{% endif %}>
                                    {{ district.name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="col-md-3">
                            <label class="form-label">Local</label>
                            <select name="local" class="form-select">
                                <option value="">All Locals</option>
                                {% for local in locals %}
                                <option value="{{ local.lcode }}" {% if current_local == local.lcode %}selected{% endif %}>
                                    {{ local.name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="col-md-2">
                            <label class="form-label">Location</label>
                            <select name="location" class="form-select">
                                <option value="">All Locations</option>
                                {% for loc in locations %}
                                <option value="{{ loc }}" {% if current_location == loc %}selected{% endif %}>
                                    {{ loc }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="col-md-2 d-flex align-items-end">
                            <button type="submit" class="btn btn-outline-primary me-2">Filter</button>
                            <a href="{% url 'kagamitan:item_list' %}" class="btn btn-outline-secondary">
                                <i class="fas fa-times"></i>
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Items Table -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Item List</h5>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped table-hover mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>Prop No.</th>
                                <th>Item Name</th>
                                <th>Brand/Model</th>
                                <th>Qty</th>
                                <th>Location</th>
                                <th>Local</th>
                                <th>Acquired</th>
                                <th class="text-end">Total Price</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in items %}
                            <tr>
                                <td><span class="badge bg-secondary">{{ item.property_number }}</span></td>
                                <td>
                                    <strong>{{ item.item_name }}</strong>
                                    {% if item.material %}
                                    <div class="small text-muted">{{ item.material }}</div>
                                    {% endif %}
                                </td>
                                <td>
                                    {{ item.brand }}
                                    {% if item.model %} / {{ item.model }}{% endif %}
                                </td>
                                <td>{{ item.quantity }}</td>
                                <td>{{ item.location }}</td>
                                <td>{{ item.local.name|default:"-" }}</td>
                                <td>{{ item.date_acquired|date:"M Y"|default:"-" }}</td>
                                <td class="text-end">₱{{ item.total_price|floatformat:2 }}</td>
                                <td>
                                    <a href="{% url 'kagamitan:item_detail' item.pk %}"
                                        class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="9" class="text-center py-4">No items found.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

with open('c:/Projects/p7project/property_management/templates/gusali/building_list.html', 'w', encoding='utf-8') as f:
    f.write(building_list_content)
    print('Fixed building_list.html')

with open('c:/Projects/p7project/property_management/templates/kagamitan/item_list.html', 'w', encoding='utf-8') as f:
    f.write(item_list_content)
    print('Fixed item_list.html')
