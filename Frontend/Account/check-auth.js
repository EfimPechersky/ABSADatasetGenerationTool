// check-auth.js - проверка авторизации для защищенных страниц
const API_BASE = 'http://127.0.0.1:8000';

console.log('check-auth.js loaded');

// Функция для декодирования JWT (если используется JWT)
function parseJWT(token) {
    if (!token) return null;
    
    try {
        const base64Url = token.split('.')[1];
        if (!base64Url) return null;
        
        let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        while (base64.length % 4) base64 += '=';
        
        const jsonString = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        return JSON.parse(jsonString);
    } catch (error) {
        console.error('Ошибка парсинга JWT:', error);
        return null;
    }
}

// Проверка валидности токена (для UUID формата)
function isTokenValid(token) {
    if (!token) return false;
    
    // Проверка на UUID формат
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    const isValidUuid = uuidRegex.test(token);
    
    if (isValidUuid) {
        console.log('Token is valid UUID');
        return true;
    }
    
    // Попытка распарсить как JWT
    try {
        const payload = parseJWT(token);
        if (payload && payload.exp) {
            const currentTime = Math.floor(Date.now() / 1000);
            const isValid = payload.exp > currentTime;
            console.log('JWT token valid:', isValid);
            return isValid;
        }
    } catch (error) {
        console.error('Token validation error:', error);
    }
    
    return false;
}

function getAuthToken() {
    console.log('getAuthToken: called');
    const accountInfoStr = localStorage.getItem('account_info');
    console.log('getAuthToken: account_info =', accountInfoStr);
    
    if (!accountInfoStr) return null;
    
    try {
        const accountInfo = JSON.parse(accountInfoStr);
        const token = accountInfo.access_token;
        console.log('getAuthToken: token found =', token ? 'yes' : 'no');
        
        if (!token) {
            localStorage.removeItem('account_info');
            return null;
        }
        
        return token;
    } catch (error) {
        console.error('getAuthToken error:', error);
        localStorage.removeItem('account_info');
        return null;
    }
}

function getCurrentUser() {
    const accountInfoStr = localStorage.getItem('account_info');
    if (!accountInfoStr) return null;
    
    try {
        const accountInfo = JSON.parse(accountInfoStr);
        if (!accountInfo.access_token) {
            localStorage.removeItem('account_info');
            return null;
        }
        return accountInfo;
    } catch (error) {
        localStorage.removeItem('account_info');
        return null;
    }
}

function checkAuth() {
    console.log('checkAuth: called');
    const token = getAuthToken();
    console.log('checkAuth: token =', token ? 'exists' : 'null');
    
    if (!token) {
        const currentPath = window.location.pathname;
        console.log('checkAuth: no token, redirecting to login from', currentPath);
        window.location.href = '../Account/Login.html';
        return null;
    }
    
    return token;
}

// Функция authFetch для выполнения авторизованных запросов
async function authFetch(url, options = {}) {
    console.log('authFetch: called with url:', url);
    const token = getAuthToken();
    
    if (!token) {
        console.log('authFetch: no token, redirecting to login');
        const currentPath = window.location.pathname;
        if (!currentPath.includes('Login.html') && !currentPath.includes('Registration.html')) {
            window.location.href = '../Account/Login.html';
        }
        throw new Error('No auth token');
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    console.log('authFetch: making request with token');
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    console.log('authFetch: response status:', response.status);
    
    if (response.status === 401 || response.status === 403) {
        console.log('authFetch: unauthorized, removing token');
        localStorage.removeItem('account_info');
        const currentPath = window.location.pathname;
        if (!currentPath.includes('Login.html') && !currentPath.includes('Registration.html')) {
            window.location.href = '../Account/Login.html';
        }
        throw new Error('Session expired');
    }
    
    return response;
}

// Функция для выхода
function logout() {
    console.log('logout: called');
    localStorage.removeItem('account_info');
    sessionStorage.clear();
    window.location.href = '../Account/Login.html';
}

// Экспортируем функции в глобальную область
window.parseJWT = parseJWT;
window.isTokenValid = isTokenValid;
window.getAuthToken = getAuthToken;
window.getCurrentUser = getCurrentUser;
window.checkAuth = checkAuth;
window.authFetch = authFetch;
window.logout = logout;
window.API_BASE = API_BASE;

console.log('check-auth.js: all functions exported');