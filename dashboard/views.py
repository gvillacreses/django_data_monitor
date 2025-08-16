from datetime import datetime, timedelta
import pytz
import json

from django.shortcuts import render
import requests
from django.conf import settings

from django.contrib.auth.decorators import login_required, permission_required


@login_required
@permission_required('dashboard.index_viewer', raise_exception=True)
def index(request):
    try:
        response = requests.get(settings.API_URL)
        posts = response.json()
    except Exception:
        posts = {}

    tz = pytz.timezone('America/Chicago')
    now = datetime.now(tz).replace(minute=0, second=0, microsecond=0)
    now_hour = now.strftime('%H:%M')

    times = posts.get('hourly', {}).get('time', [])
    temperatures = posts.get('hourly', {}).get('temperature_2m', [])
    apparent_temperatures = posts.get('hourly', {}).get('apparent_temperature', [])
    wind_speeds = posts.get('hourly', {}).get('wind_speed_10m', [])
    humidities = posts.get('hourly', {}).get('relative_humidity_2m', [])

    table_rows = []
    seen_dates = set()
    for i, time_str in enumerate(times):
        dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
        date_str = dt.strftime('%Y-%m-%d')
        hour_str = dt.strftime('%H:%M')
        if hour_str == now_hour and date_str not in seen_dates:
            seen_dates.add(date_str)
            if date_str == now.strftime('%Y-%m-%d'):
                dia = "actual"
            elif date_str == (now + timedelta(days=1)).strftime('%Y-%m-%d'):
                dia = "mañana"
            else:
                dia = dt.strftime('%d de %B').replace('January', 'enero').replace('February', 'febrero').replace('March', 'marzo').replace('April', 'abril').replace('May', 'mayo').replace('June', 'junio').replace('July', 'julio').replace('August', 'agosto').replace('September', 'septiembre').replace('October', 'octubre').replace('November', 'noviembre').replace('December', 'diciembre')
            table_rows.append({
                'dia': dia,
                'hora': hour_str,
                'temperatura': temperatures[i] if i < len(temperatures) else None,
                'aparente': apparent_temperatures[i] if i < len(apparent_temperatures) else None,
                'viento': wind_speeds[i] if i < len(wind_speeds) else None,
                'humedad': humidities[i] if i < len(humidities) else None,
            })

    try:
        now_str = now.strftime('%Y-%m-%dT%H:%M')
        idx = times.index(now_str)
        current_temperature = temperatures[idx] if idx < len(temperatures) else None
        current_apparent_temperature = apparent_temperatures[idx] if idx < len(apparent_temperatures) else None
        current_wind_speed = wind_speeds[idx] if idx < len(wind_speeds) else None
        current_humidity = humidities[idx] if idx < len(humidities) else None
    except (ValueError, IndexError):
        current_temperature = None
        current_apparent_temperature = None
        current_wind_speed = None
        current_humidity = None

    
    # Filtra temperaturas y aparentes solo para el día actual
    horas_actual = []
    temps_actual = []
    temps_aparentes_actual = []
    fecha_actual = now.strftime('%Y-%m-%d')
    for i, time_str in enumerate(times):
        if time_str.startswith(fecha_actual):
            dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
            horas_actual.append(dt.strftime('%H:%M'))
            temps_actual.append(temperatures[i] if i < len(temperatures) else None)
            temps_aparentes_actual.append(apparent_temperatures[i] if i < len(apparent_temperatures) else None)

    data = {
        'title': "Dashboard",
        'temperature': current_temperature,
        'apparent_temperature': current_apparent_temperature,
        'wind_speed': current_wind_speed,
        'relative_humidity': current_humidity,
        'table_rows': table_rows,
        'horas_actual_json': json.dumps(horas_actual),
        'temps_actual_json': json.dumps(temps_actual),
        'temps_aparentes_actual_json': json.dumps(temps_aparentes_actual),
    }

    return render(request, 'dashboard/index.html', data)