// Текущая дата для ограничения выбора
document.getElementById('id_date').min = new Date().toISOString().split('T')[0];

// Функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Получаем данные из HTML
    const reservationData = document.getElementById('reservation-data');
    const AVAILABLE_TIMES_URL = reservationData.dataset.availableTimesUrl;
    const RESERVATION_URL = reservationData.dataset.reservationUrl;
    const CSRF_TOKEN = reservationData.dataset.csrfToken;

    // Инициализация страницы
    initializePage();

    function initializePage() {
        // Загружаем временные слоты при загрузке страницы
        const date = document.getElementById('id_date').value;
        const guests = document.getElementById('id_guests_count').value;
        if (date && guests) {
            loadAvailableTimes(date, guests);
        }
        
        // Привязываем обработчики для столиков
        bindTableEvents();
        
        // Привязываем обработчики для временных слотов
        bindTimeSlotEvents();
        
        // Устанавливаем минимальную дату
        document.getElementById('id_date').min = new Date().toISOString().split('T')[0];
    }

    function loadAvailableTimes(date, guestsCount) {
        if (!date || !guestsCount) {
            console.error('Missing date or guests count');
            return;
        }
        
        const formData = new FormData();
        formData.append('date', date);
        formData.append('guests_count', guestsCount);
        
        fetch(AVAILABLE_TIMES_URL, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': CSRF_TOKEN
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Server error:', data.error);
                return;
            }
            if (data.available_hours) {
                updateTimeSlots(data.available_hours);
            }
        })
        .catch(error => console.error('Error loading available times:', error));
    }

    // Остальные функции (updateTimeSlots, bindTableEvents и т.д.)
    // ...
});

// Функция для загрузки доступных временных слотов
function loadAvailableTimes(date, guestsCount) {
    if (!date || !guestsCount) {
        console.error('Missing date or guests count');
        return;
    }
    
    const formData = new FormData();
    formData.append('date', date);
    formData.append('guests_count', guestsCount);
    
    fetch('{% url "restaurant:get_available_times" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Server error:', data.error);
            return;
        }
        if (data.available_hours) {
            updateTimeSlots(data.available_hours);
        }
    })
    .catch(error => console.error('Error loading available times:', error));
}

// Функция для обновления отображения временных слотов
function updateTimeSlots(hours) {
    const timeSlotsContainer = document.getElementById('timeSlots');
    if (!timeSlotsContainer) return;
    
    timeSlotsContainer.innerHTML = '';
    
    hours.forEach(hour => {
        const timeSlot = document.createElement('div');
        timeSlot.className = 'col-4 col-sm-3 mb-2';
        timeSlot.innerHTML = `
            <div class="card time-slot text-center p-2 ${hour.available ? '' : 'bg-secondary text-white'}" 
                 data-time="${hour.time}">
                ${hour.time}
            </div>
        `;
        timeSlotsContainer.appendChild(timeSlot);
    });
    
    // Перепривязываем обработчики событий к новым элементам
    bindTimeSlotEvents();
}

// Функция для привязки обработчиков событий к временным слотам
function bindTimeSlotEvents() {
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.addEventListener('click', function() {
            if (!this.classList.contains('bg-secondary')) {
                document.querySelectorAll('.time-slot').forEach(s => {
                    s.classList.remove('bg-primary', 'text-white');
                });
                this.classList.add('bg-primary', 'text-white');
                
                // Сохраняем выбранное время в скрытое поле
                document.getElementById('id_time').value = this.dataset.time;
            }
        });
    });
}

// Функция для привязки обработчиков событий к столикам
function bindTableEvents() {
    console.log('Binding table events...');
    console.log('Total tables found:', document.querySelectorAll('.table-card').length);
    
    document.querySelectorAll('.table-card').forEach(table => {
        console.log('Table ID:', table.dataset.tableId, 
                   'Data available:', table.dataset.available,
                   'Type:', typeof table.dataset.available);
        
        table.addEventListener('click', function() {
            console.log('Clicked - Available value:', this.dataset.available, 'Type:', typeof this.dataset.available);
            console.log('Strict comparison with "true":', this.dataset.available === 'true');
            console.log('Loose comparison with true:', this.dataset.available == true);
            
            if (this.dataset.available === 'true') {
                console.log('Table is available, proceeding...');
                document.querySelectorAll('.table-card').forEach(t => {
                    t.classList.remove('selected');
                });
                this.classList.add('selected');
                
                document.getElementById('id_table').value = this.dataset.tableId;
                console.log('Selected table:', this.dataset.tableId);
            } else {
                console.log('Table is not available:', this.dataset.tableId);
                alert('Этот столик занят. Пожалуйста, выберите другой.');
            }
        });
    });
}

// Загружаем временные слоты при изменении даты или количества гостей
document.getElementById('id_date').addEventListener('change', function() {
    const date = this.value;
    const guests = document.getElementById('id_guests_count').value;
    if (date && guests) {
        loadAvailableTimes(date, guests);
    }
});

document.getElementById('id_guests_count').addEventListener('change', function() {
    const date = document.getElementById('id_date').value;
    const guests = this.value;
    if (date && guests) {
        loadAvailableTimes(date, guests);
    }
});

// Обновляем информацию о выбранной дате и количестве гостей
document.getElementById('id_date').addEventListener('change', updateSelectionInfo);
document.getElementById('id_guests_count').addEventListener('change', updateSelectionInfo);

function updateSelectionInfo() {
    const date = document.getElementById('id_date').value;
    const guests = document.getElementById('id_guests_count').value;
    
    if (date) {
        const formattedDate = new Date(date).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'long'
        });
        document.getElementById('selectedDateTime').textContent = formattedDate;
    }
    
    if (guests) {
        document.getElementById('selectedGuests').textContent = guests + ' гостей';
    }
}

// Функция для отправки шага 1
function submitStep1() {
    const timeSlot = document.querySelector('.time-slot.bg-primary');
    
    if (!timeSlot) {
        alert('Пожалуйста, выберите время');
        return;
    }
    
    const formData = new FormData(document.getElementById('step1Form'));
    
    fetch('{% url "restaurant:reservation" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showStep(2);
        } else {
            alert('Ошибки: ' + JSON.stringify(data.errors));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке формы');
    });
}

// Функция для отправки шага 2
function submitStep2() {
    const selectedTable = document.querySelector('.table-card.selected');
    
    if (!selectedTable) {
        alert('Пожалуйста, выберите столик');
        return;
    }
    
    const formData = new FormData(document.getElementById('step2Form'));
    
    fetch('{% url "restaurant:reservation" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showStep(3);
        } else {
            alert('Ошибки: ' + JSON.stringify(data.errors));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке формы');
    });
}

// Обработка формы шага 3
document.getElementById('step3Form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Проверяем соглашение
    const agreement = document.getElementById('agreement');
    if (!agreement.checked) {
        alert('Пожалуйста, согласитесь с правилами бронирования');
        return;
    }
    
    const formData = new FormData(this);
    
    fetch('{% url "restaurant:reservation" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Заполняем модальное окно данными
            document.getElementById('modalDate').textContent = data.reservation.date + ' ' + data.reservation.time;
            document.getElementById('modalGuests').textContent = data.reservation.guests_count + ' гостя';
            document.getElementById('modalTable').textContent = 'Столик ' + data.reservation.table_number + ' (' + data.reservation.table_description + ')';
            document.getElementById('modalName').textContent = data.reservation.client_name;
            document.getElementById('modalPhone').textContent = data.reservation.client_phone;
            
            if (data.reservation.client_email) {
                document.getElementById('modalEmail').textContent = data.reservation.client_email;
                document.getElementById('modalEmailContainer').style.display = 'flex';
            }
            
            if (data.reservation.special_requests) {
                document.getElementById('modalRequests').textContent = data.reservation.special_requests;
                document.getElementById('modalRequestsContainer').style.display = 'flex';
            }
            
            // Показываем модальное окно
            var reservationModal = new bootstrap.Modal(document.getElementById('reservationModal'));
            reservationModal.show();
        } else {
            alert('Ошибки: ' + JSON.stringify(data.errors));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке формы');
    });
});

// Функция переключения между шагами
function showStep(stepNumber) {
    document.querySelectorAll('.confirmation-step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById('step' + stepNumber).classList.add('active');
    
    // Обновление индикатора прогресса
    document.querySelectorAll('.progress-divider').forEach((divider, index) => {
        if (index < stepNumber - 1) {
            divider.classList.add('bg-primary');
        } else {
            divider.classList.remove('bg-primary');
        }
    });
    
    document.querySelectorAll('.badge.rounded-circle').forEach((badge, index) => {
        if (index < stepNumber) {
            badge.classList.add('bg-primary');
            badge.classList.remove('bg-secondary');
        } else {
            badge.classList.remove('bg-primary');
            badge.classList.add('bg-secondary');
        }
    });
}