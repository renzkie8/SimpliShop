/* ============================================
   SimpliShop - Shared JS
   Auth + Cart + Search + UI components
   ============================================ */

/* ---------- AUTH (session-based) ---------- */
const Auth = {
  KEY: 'simplishop_user',
  getUser() {
    try { return JSON.parse(sessionStorage.getItem(this.KEY)) || null; }
    catch (e) { return null; }
  },
  setUser(user) { sessionStorage.setItem(this.KEY, JSON.stringify(user)); },
  signOut() { sessionStorage.removeItem(this.KEY); },
  isLoggedIn() { return !!this.getUser(); },
  displayName() {
    const u = this.getUser();
    if (!u) return null;
    if (u.name) return u.name.split(' ')[0];
    if (u.email) return u.email.split('@')[0];
    return 'Friend';
  }
};

/* ---------- CART (session-based) ---------- */
const Cart = {
  KEY: 'simplishop_cart',
  getItems() {
    try { return JSON.parse(sessionStorage.getItem(this.KEY)) || []; }
    catch (e) { return []; }
  },
  setItems(items) {
    sessionStorage.setItem(this.KEY, JSON.stringify(items));
    document.dispatchEvent(new CustomEvent('cart:changed'));
  },
  add(product) {
    const items = this.getItems();
    const existing = items.find(i => i.id === product.id);
    if (existing) {
      existing.qty = (existing.qty || 1) + 1;
    } else {
      items.push({
        id: product.id,
        title: product.title,
        price: product.price,
        priceStrike: product.priceStrike || null,
        image: product.image || '',
        qty: 1
      });
    }
    this.setItems(items);
  },
  remove(id) {
    this.setItems(this.getItems().filter(i => i.id !== id));
  },
  updateQty(id, qty) {
    const items = this.getItems();
    const item = items.find(i => i.id === id);
    if (item) item.qty = Math.max(1, parseInt(qty, 10) || 1);
    this.setItems(items);
  },
  count() {
    return this.getItems().reduce((s, i) => s + (i.qty || 1), 0);
  },
  total() {
    return this.getItems().reduce((s, i) => s + (i.price * (i.qty || 1)), 0);
  },
  clear() { sessionStorage.removeItem(this.KEY); document.dispatchEvent(new CustomEvent('cart:changed')); }
};

/* ---------- FORMATTERS ---------- */
function peso(n) {
  return '₱' + Math.round(n).toLocaleString('en-PH');
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

/* ---------- HEADER STATE ---------- */
function refreshHeader() {
  document.querySelectorAll('.header-greeting').forEach(el => {
    if (Auth.isLoggedIn()) {
      el.innerHTML = `Welcome, <strong>${escapeHtml(Auth.displayName())}!</strong>`;
    } else {
      el.innerHTML = `Hello, <a href="signin.html">sign in</a>`;
    }
  });
  document.querySelectorAll('.account-link').forEach(el => {
    el.setAttribute('href', Auth.isLoggedIn() ? '#' : 'signin.html');
  });
  const count = Cart.count();
  document.querySelectorAll('.cart-count-badge').forEach(el => {
    if (count > 0) {
      el.textContent = count > 99 ? '99+' : count;
      el.style.display = 'flex';
    } else {
      el.style.display = 'none';
    }
  });
}

/* ---------- ACCOUNT MENU ---------- */
function setupAccountMenu() {
  document.querySelectorAll('.account-link').forEach(link => {
    link.addEventListener('click', (e) => {
      if (!Auth.isLoggedIn()) return;
      e.preventDefault();
      let menu = link.parentElement.querySelector('.account-menu');
      if (!menu) {
        menu = document.createElement('div');
        menu.className = 'account-menu';
        const u = Auth.getUser();
        menu.innerHTML = `
          <div class="account-menu-header">
            <div class="account-name">${escapeHtml(u.name || u.email || 'Friend')}</div>
            ${u.email ? `<div class="account-email">${escapeHtml(u.email)}</div>` : ''}
          </div>
          <a href="#" class="account-menu-item">Your Orders</a>
          <a href="#" class="account-menu-item">Your Account</a>
          <a href="#" class="account-menu-item sign-out">Sign Out</a>
        `;
        link.parentElement.style.position = 'relative';
        link.parentElement.appendChild(menu);
        menu.querySelector('.sign-out').addEventListener('click', (ev) => {
          ev.preventDefault();
          Auth.signOut();
          window.location.href = 'index.html';
        });
      }
      menu.classList.toggle('active');
      const closeFn = (ev) => {
        if (!menu.contains(ev.target) && ev.target !== link && !link.contains(ev.target)) {
          menu.classList.remove('active');
          document.removeEventListener('click', closeFn);
        }
      };
      setTimeout(() => document.addEventListener('click', closeFn), 0);
    });
  });
}

/* ---------- PASSWORD TOGGLE ---------- */
const eyeSVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
const eyeOffSVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';

function setupPasswordToggle() {
  document.querySelectorAll('.toggle-pwd').forEach(btn => {
    btn.addEventListener('click', () => {
      const wrapper = btn.closest('.input-wrapper');
      const input = wrapper.querySelector('input');
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.innerHTML = isHidden ? eyeOffSVG : eyeSVG;
    });
  });
}

/* ---------- SEARCH DROPDOWN ---------- */
const ALL_SUGGESTIONS = [
  { text: 'wireless noise cancelling headphones', target: 'search-headphones.html' },
  { text: 'wireless noise cancelling headphones sony', target: 'search-headphones.html' },
  { text: 'wireless noise cancelling headphones bose', target: 'search-headphones.html' },
  { text: 'wireless earbuds', target: 'search-headphones.html' },
  { text: 'wireless headphones with mic', trending: true, target: 'search-headphones.html' },
  { text: 'wireless gaming headset', trending: true, target: 'search-headphones.html' },
  { text: 'bluetooth headphones', target: 'search-headphones.html' },
  { text: 'over ear wireless headphones', target: 'search-headphones.html' },
  { text: 'iphone 15 pro max', target: 'search-smartphones.html' },
  { text: 'samsung galaxy s24 ultra', target: 'search-smartphones.html' },
  { text: 'samsung galaxy', target: 'search-smartphones.html' },
  { text: 'pixel 8 pro', target: 'search-smartphones.html' },
  { text: 'oneplus 12', target: 'search-smartphones.html' },
  { text: 'smartphone deals', trending: true, target: 'search-smartphones.html' },
  { text: 'budget smartphone', target: 'search-smartphones.html' },
  { text: 'smartphone with best camera', target: 'search-smartphones.html' },
  { text: 'cotton t-shirt', target: 'search-clothes.html' },
  { text: 'denim jacket', target: 'search-clothes.html' },
  { text: 'summer dress', target: 'search-clothes.html' },
  { text: 'hoodie unisex', target: 'search-clothes.html' },
  { text: 'minimalist clothing', trending: true, target: 'search-clothes.html' },
  { text: 'streetwear hoodie', target: 'search-clothes.html' },
  { text: 'jeans slim fit', target: 'search-clothes.html' },
  { text: 'oversized t-shirt', target: 'search-clothes.html' }
];

const SEARCH_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
const TREND_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>';

function filterSuggestions(query) {
  const q = (query || '').trim().toLowerCase();
  if (!q) return [];
  const starts = [];
  const contains = [];
  ALL_SUGGESTIONS.forEach(s => {
    const t = s.text.toLowerCase();
    if (t.startsWith(q)) starts.push(s);
    else if (t.includes(q)) contains.push(s);
  });
  return [...starts, ...contains].slice(0, 8);
}

function renderDropdown(dropdown, suggestions) {
  if (!suggestions.length) {
    dropdown.innerHTML = `<div class="search-dropdown-empty">No suggestions yet. Press Enter to search anyway.</div>`;
    return;
  }
  dropdown.innerHTML = suggestions.map((s) => {
    const iconClass = s.trending ? 'icon-wrap trend' : 'icon-wrap';
    const icon = s.trending ? TREND_ICON : SEARCH_ICON;
    const tag = s.trending ? '<span class="trending-tag">Trending</span>' : '';
    return `<a href="${s.target}" class="search-dropdown-item">
      <span class="${iconClass}">${icon}</span>
      <span class="label">${escapeHtml(s.text)}</span>
      ${tag}
    </a>`;
  }).join('');
}

function bestSearchTarget(query) {
  const q = (query || '').trim().toLowerCase();
  if (!q) return 'search-headphones.html';
  const matches = filterSuggestions(q);
  if (matches.length) return matches[0].target;
  if (q.match(/phone|iphone|samsung|pixel|smartphone|android/)) return 'search-smartphones.html';
  if (q.match(/shirt|dress|hoodie|jacket|jean|pant|cloth|wear|fashion/)) return 'search-clothes.html';
  return 'search-headphones.html';
}

function setupSearchDropdown() {
  const searchBars = document.querySelectorAll('.search-bar');
  if (!searchBars.length) return;

  let overlay = document.querySelector('.search-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'search-overlay';
    document.body.appendChild(overlay);
  }

  searchBars.forEach(bar => {
    const input = bar.querySelector('input');
    const submitBtn = bar.querySelector('button');
    if (!input) return;

    input.value = '';
    input.removeAttribute('value');
    input.setAttribute('autocomplete', 'off');
    if (!input.getAttribute('placeholder')) input.setAttribute('placeholder', 'Search SimpliShop');

    let dropdown = bar.querySelector('.search-dropdown');
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.className = 'search-dropdown';
      bar.appendChild(dropdown);
    }
    dropdown.innerHTML = '';

    const open = () => {
      const q = input.value;
      if (!q.trim()) {
        close();
        return;
      }
      renderDropdown(dropdown, filterSuggestions(q));
      dropdown.classList.add('active');
      overlay.classList.add('active');
      bar.classList.add('dropdown-open');
    };
    const close = () => {
      dropdown.classList.remove('active');
      overlay.classList.remove('active');
      bar.classList.remove('dropdown-open');
    };

    input.addEventListener('focus', open);
    input.addEventListener('input', open);

    if (submitBtn) {
      submitBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const q = input.value.trim();
        if (q.length > 0) window.location.href = bestSearchTarget(q);
      });
    }
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const q = input.value.trim();
        if (q.length > 0) window.location.href = bestSearchTarget(q);
      } else if (e.key === 'Escape') {
        input.blur();
        close();
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-bar')) close();
    });
    overlay.addEventListener('click', close);
  });
}

/* ---------- ADD TO CART ---------- */
function setupAddToCart() {
  document.querySelectorAll('[data-add-to-cart]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const prod = {
        id: btn.dataset.id,
        title: btn.dataset.title,
        price: parseFloat(btn.dataset.price),
        priceStrike: btn.dataset.priceStrike ? parseFloat(btn.dataset.priceStrike) : null,
        image: btn.dataset.image || ''
      };
      Cart.add(prod);
      const original = btn.innerHTML;
      btn.classList.add('added');
      btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Added';
      setTimeout(() => {
        btn.innerHTML = original;
        btn.classList.remove('added');
      }, 1100);
    });
  });
}

/* ---------- QUANTITY SELECTORS ---------- */
function setupQtySelectors() {
  document.querySelectorAll('.qty-selector').forEach(selector => {
    if (selector.dataset.bound) return;
    selector.dataset.bound = '1';
    const minus = selector.querySelector('.qty-minus');
    const plus = selector.querySelector('.qty-plus');
    const input = selector.querySelector('input');
    if (!minus || !plus || !input) return;
    const id = selector.dataset.cartId;

    minus.addEventListener('click', () => {
      const v = parseInt(input.value) || 1;
      if (v > 1) {
        input.value = v - 1;
        if (id) { Cart.updateQty(id, v - 1); renderCartIfPresent(); }
      }
    });
    plus.addEventListener('click', () => {
      const v = parseInt(input.value) || 1;
      input.value = v + 1;
      if (id) { Cart.updateQty(id, v + 1); renderCartIfPresent(); }
    });
  });
}

/* ---------- CART PAGE RENDER ---------- */
function renderCartIfPresent() {
  const list = document.querySelector('.cart-items');
  if (!list) return;
  const items = Cart.getItems();
  const itemCountEl = document.querySelector('.item-count');
  const subtotalEl = document.querySelector('[data-cart-subtotal]');
  const totalEl = document.querySelector('[data-cart-total]');
  const shippingEl = document.querySelector('[data-cart-shipping]');
  const summarySubEl = document.querySelector('[data-cart-summary-sub]');

  if (items.length === 0) {
    list.innerHTML = `
      <div class="cart-empty">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
        <h3>Your cart is empty</h3>
        <p>Looks like you haven't added anything yet.</p>
        <a href="index.html" class="btn btn-primary">Start Shopping</a>
      </div>
    `;
    if (itemCountEl) itemCountEl.textContent = '(0 items)';
    if (subtotalEl) subtotalEl.textContent = peso(0);
    if (totalEl) totalEl.textContent = peso(0);
    if (shippingEl) shippingEl.textContent = peso(0);
    if (summarySubEl) summarySubEl.textContent = '0 items in your cart';
    const proceed = document.querySelector('.proceed-checkout-btn');
    if (proceed) { proceed.classList.add('disabled'); proceed.setAttribute('href', '#'); }
    return;
  }

  list.innerHTML = items.map(item => {
    const subtotal = item.price * (item.qty || 1);
    const savings = item.priceStrike ? (item.priceStrike - item.price) * (item.qty || 1) : 0;
    return `
      <div class="cart-item">
        <div class="cart-item-image">
          ${item.image
            ? `<img src="${item.image}" alt="${escapeHtml(item.title)}" onerror="this.parentElement.classList.add('img-fallback');this.remove();">`
            : ''}
        </div>
        <div class="cart-item-info">
          <h3>${escapeHtml(item.title)}</h3>
          <div class="in-stock">In Stock</div>
          <div class="free-delivery">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
            <strong>Eligible for FREE Delivery</strong>
          </div>
          <div class="cart-item-price-row">
            <span class="price">${peso(item.price)}</span>
            ${item.priceStrike ? `<span class="price-strike">${peso(item.priceStrike)}</span>` : ''}
          </div>
          ${savings > 0 ? `<div class="savings">Save ${peso(savings)}</div>` : ''}
          <div class="cart-item-controls" style="margin-top:10px;">
            <span class="qty-label">Qty:</span>
            <div class="qty-selector" data-cart-id="${escapeHtml(item.id)}">
              <button class="qty-minus" aria-label="Decrease">−</button>
              <input type="text" value="${item.qty}" readonly>
              <button class="qty-plus" aria-label="Increase">+</button>
            </div>
            <button class="remove-btn" data-remove-id="${escapeHtml(item.id)}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              Remove
            </button>
          </div>
        </div>
        <div class="cart-item-subtotal">
          Subtotal:
          <span class="subtotal-amount">${peso(subtotal)}</span>
        </div>
      </div>
    `;
  }).join('');

  const sub = Cart.total();
  const shipping = sub > 50000 ? 0 : 316;
  const total = sub + shipping;

  if (itemCountEl) itemCountEl.textContent = `(${Cart.count()} ${Cart.count() === 1 ? 'item' : 'items'})`;
  if (subtotalEl) subtotalEl.textContent = peso(sub);
  if (totalEl) totalEl.textContent = peso(total);
  if (shippingEl) shippingEl.innerHTML = shipping === 0 ? '<span style="color:var(--success-green);font-weight:700;">FREE</span>' : peso(shipping);
  if (summarySubEl) summarySubEl.textContent = `${Cart.count()} ${Cart.count() === 1 ? 'item' : 'items'} in your cart`;

  const proceed = document.querySelector('.proceed-checkout-btn');
  if (proceed) { proceed.classList.remove('disabled'); proceed.setAttribute('href', 'checkout-shipping.html'); }

  setupQtySelectors();
  document.querySelectorAll('[data-remove-id]').forEach(btn => {
    btn.addEventListener('click', () => {
      Cart.remove(btn.dataset.removeId);
      renderCartIfPresent();
    });
  });
}

/* ---------- CHECKOUT SUMMARY RENDER ---------- */
function renderCheckoutSummary() {
  const wrap = document.querySelector('[data-checkout-summary]');
  if (!wrap) return;
  const sub = Cart.total();
  const tax = Math.round(sub * 0.18);
  const shipping = 0;
  const total = sub + tax + shipping;

  const subEl = wrap.querySelector('[data-checkout-sub]');
  const taxEl = wrap.querySelector('[data-checkout-tax]');
  const totalEl = wrap.querySelector('[data-checkout-total]');
  const itemsCountEl = wrap.querySelector('[data-checkout-itemcount]');
  if (subEl) subEl.textContent = peso(sub);
  if (taxEl) taxEl.textContent = peso(tax);
  if (totalEl) totalEl.textContent = peso(total);
  if (itemsCountEl) itemsCountEl.textContent = `Items (${Cart.count()}):`;

  // Confirm step review list
  const reviewList = document.querySelector('[data-review-list]');
  if (reviewList) {
    const items = Cart.getItems();
    if (items.length === 0) {
      reviewList.innerHTML = '<div class="muted" style="padding:14px 0;">Your cart is empty.</div>';
    } else {
      reviewList.innerHTML = items.map(item => `
        <div class="review-item">
          <div class="review-image">
            ${item.image ? `<img src="${item.image}" alt="${escapeHtml(item.title)}" onerror="this.parentElement.classList.add('img-fallback');this.remove();">` : ''}
          </div>
          <div class="review-info">
            <h4>${escapeHtml(item.title)}</h4>
            <div class="qty">Qty: ${item.qty}</div>
          </div>
          <div class="review-price">${peso(item.price * item.qty)}</div>
        </div>
      `).join('');
    }
  }
}

/* ---------- COMPARE BAR + MODAL ---------- */
function getComparedItems() {
  return Array.from(document.querySelectorAll('.compare-cell input[type=checkbox]:checked'))
    .map(cb => {
      const item = cb.closest('.result-item');
      if (!item) return null;
      const titleEl = item.querySelector('h3');
      const priceEl = item.querySelector('.price');
      const ratingEl = item.querySelector('.rating-text');
      const reviewEl = item.querySelector('.review-count');
      const imgEl = item.querySelector('.result-image img');
      const features = Array.from(item.querySelectorAll('.result-features li')).map(li => li.textContent.trim());
      return {
        title: titleEl ? titleEl.textContent.trim() : '',
        price: priceEl ? priceEl.textContent.trim() : '',
        rating: ratingEl ? ratingEl.textContent.trim() : '',
        reviews: reviewEl ? reviewEl.textContent.trim() : '',
        image: imgEl ? imgEl.getAttribute('src') : '',
        features: features
      };
    })
    .filter(Boolean);
}

function setupCompare() {
  const checkboxes = document.querySelectorAll('.compare-cell input[type=checkbox]');
  const bar = document.querySelector('.compare-bar');
  const counter = document.querySelector('.compare-bar .compare-count');
  const compareBtn = document.querySelector('.compare-bar .btn-compare-go');

  function update() {
    const count = document.querySelectorAll('.compare-cell input[type=checkbox]:checked').length;
    if (bar) {
      if (count > 0) {
        bar.style.display = 'flex';
        if (counter) counter.textContent = count;
        if (compareBtn) {
          compareBtn.disabled = count < 2;
          compareBtn.classList.toggle('disabled', count < 2);
        }
      } else {
        bar.style.display = 'none';
      }
    }
  }
  checkboxes.forEach(cb => cb.addEventListener('change', update));
  update();

  checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      const checked = document.querySelectorAll('.compare-cell input[type=checkbox]:checked').length;
      if (checked > 4) {
        cb.checked = false;
        alert('You can compare up to 4 products at a time.');
        update();
      }
    });
  });

  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      const items = getComparedItems();
      if (items.length < 2) return;
      openCompareModal(items);
    });
  }
}

function openCompareModal(items) {
  let modal = document.querySelector('.compare-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.className = 'compare-modal';
    document.body.appendChild(modal);
  }
  const rows = [
    { label: 'Product', render: i => `
      <div class="compare-product-cell">
        <div class="compare-img">
          ${i.image ? `<img src="${i.image}" alt="" onerror="this.parentElement.classList.add('img-fallback');this.remove();">` : ''}
        </div>
        <div class="compare-name">${escapeHtml(i.title)}</div>
      </div>
    `},
    { label: 'Price', render: i => `<div class="compare-price">${escapeHtml(i.price)}</div>` },
    { label: 'Rating', render: i => `
      <div class="compare-rating">
        <span class="stars">★★★★<span style="color:#ddd">★</span></span>
        <span class="rating-num">${escapeHtml(i.rating)}</span>
        <span class="muted">${escapeHtml(i.reviews)}</span>
      </div>
    `},
    { label: 'Key Features', render: i => `
      <ul class="compare-features">
        ${i.features.length ? i.features.map(f => `<li>${escapeHtml(f)}</li>`).join('') : '<li class="muted">—</li>'}
      </ul>
    `}
  ];
  const colCount = items.length;
  const colTemplate = `150px repeat(${colCount}, minmax(0, 1fr))`;

  modal.innerHTML = `
    <div class="compare-modal-overlay"></div>
    <div class="compare-modal-card">
      <div class="compare-modal-header">
        <h2>Compare Products <span class="muted">(${colCount})</span></h2>
        <button class="compare-modal-close" aria-label="Close">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="compare-modal-body">
        <div class="compare-grid" style="grid-template-columns: ${colTemplate};">
          ${rows.map(row => `
            <div class="compare-row-label">${row.label}</div>
            ${items.map(it => `<div class="compare-row-cell">${row.render(it)}</div>`).join('')}
          `).join('')}
        </div>
      </div>
      <div class="compare-modal-footer">
        <button class="btn btn-outline" data-close>Close</button>
      </div>
    </div>
  `;
  modal.classList.add('active');

  const close = () => modal.classList.remove('active');
  modal.querySelector('.compare-modal-overlay').addEventListener('click', close);
  modal.querySelector('.compare-modal-close').addEventListener('click', close);
  modal.querySelector('[data-close]').addEventListener('click', close);
  document.addEventListener('keydown', function escListener(e) {
    if (e.key === 'Escape') {
      close();
      document.removeEventListener('keydown', escListener);
    }
  });
}

/* ---------- FILTER ACCORDION ---------- */
function setupFilterAccordion() {
  document.querySelectorAll('.filter-group-header').forEach(header => {
    header.addEventListener('click', () => {
      const group = header.closest('.filter-group');
      const list = group.querySelector('.filter-list, .filter-checkbox-list');
      const arrow = header.querySelector('svg');
      if (!list) return;
      const isHidden = list.style.display === 'none';
      list.style.display = isHidden ? '' : 'none';
      if (arrow) arrow.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(180deg)';
    });
  });
}

/* ---------- FILTERS ---------- */
function setupFilters() {
  const items = document.querySelectorAll('.result-item');
  if (!items.length) return;

  function getCheckedValues(group) {
    return Array.from(document.querySelectorAll(`.filter-checkbox[data-group="${group}"] input:checked`))
      .map(c => c.value);
  }
  function priceMatches(price, range) {
    switch (range) {
      case 'under_5000': return price < 5000;
      case '5000_10000': return price >= 5000 && price <= 10000;
      case '10000_20000': return price > 10000 && price <= 20000;
      case '20000_30000': return price > 20000 && price <= 30000;
      case 'over_30000': return price > 30000;
      default: return true;
    }
  }
  function applyFilters() {
    const checked = {
      brand: getCheckedValues('brand'),
      price: getCheckedValues('price'),
      rating: getCheckedValues('rating'),
      features: getCheckedValues('features'),
      connectivity: getCheckedValues('connectivity')
    };

    let visibleCount = 0;
    items.forEach(item => {
      const data = {
        brand: (item.dataset.brand || '').toLowerCase(),
        price: parseFloat(item.dataset.price || '0'),
        rating: parseFloat(item.dataset.rating || '0'),
        features: (item.dataset.features || '').toLowerCase().split(',').map(s => s.trim()).filter(Boolean),
        connectivity: (item.dataset.connectivity || '').toLowerCase().split(',').map(s => s.trim()).filter(Boolean)
      };

      let show = true;
      if (checked.brand.length && !checked.brand.map(s => s.toLowerCase()).includes(data.brand)) show = false;
      if (show && checked.price.length) {
        const inAny = checked.price.some(range => priceMatches(data.price, range));
        if (!inAny) show = false;
      }
      if (show && checked.rating.length) {
        const minRating = Math.min(...checked.rating.map(r => parseFloat(r)));
        if (data.rating < minRating) show = false;
      }
      if (show && checked.features.length) {
        const allMatch = checked.features.every(f => data.features.includes(f.toLowerCase()));
        if (!allMatch) show = false;
      }
      if (show && checked.connectivity.length) {
        const anyMatch = checked.connectivity.some(c => data.connectivity.includes(c.toLowerCase()));
        if (!anyMatch) show = false;
      }

      item.style.display = show ? '' : 'none';
      if (show) visibleCount++;
    });

    const countEl = document.querySelector('.results-count');
    if (countEl) {
      const total = countEl.dataset.total || items.length;
      countEl.textContent = `Showing ${visibleCount} of ${total} results`;
    }
    const list = document.querySelector('.result-list');
    let empty = list ? list.querySelector('.no-results') : null;
    if (visibleCount === 0 && list) {
      if (!empty) {
        empty = document.createElement('div');
        empty.className = 'no-results';
        empty.innerHTML = `<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><h3>No results match your filters</h3><p>Try removing some filters or clearing all to see more products.</p>`;
        list.appendChild(empty);
      }
    } else if (empty) {
      empty.remove();
    }
  }

  document.querySelectorAll('.filter-checkbox input').forEach(cb => {
    cb.addEventListener('change', applyFilters);
  });

  const clear = document.querySelector('.clear-filters');
  if (clear) {
    clear.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.filter-checkbox input:checked').forEach(c => c.checked = false);
      applyFilters();
    });
  }

  const sort = document.querySelector('.sort-dropdown select');
  if (sort) {
    sort.addEventListener('change', () => {
      const list = document.querySelector('.result-list');
      if (!list) return;
      const compareBar = list.querySelector('.compare-bar');
      const arr = Array.from(items);
      const v = sort.value;
      arr.sort((a, b) => {
        const pa = parseFloat(a.dataset.price || '0');
        const pb = parseFloat(b.dataset.price || '0');
        const ra = parseFloat(a.dataset.rating || '0');
        const rb = parseFloat(b.dataset.rating || '0');
        if (v === 'price_low') return pa - pb;
        if (v === 'price_high') return pb - pa;
        if (v === 'rating') return rb - ra;
        return 0;
      });
      arr.forEach(it => list.insertBefore(it, compareBar));
    });
  }
}

/* ---------- CHECKOUT ---------- */
function setupShippingOptions() {
  document.querySelectorAll('.shipping-option').forEach(option => {
    option.addEventListener('click', () => {
      document.querySelectorAll('.shipping-option').forEach(o => o.classList.remove('selected'));
      option.classList.add('selected');
    });
  });
}
function setupPaymentOptions() {
  document.querySelectorAll('.payment-option').forEach(option => {
    option.addEventListener('click', () => {
      document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
      option.classList.add('selected');
    });
  });
}

/* ---------- AUTH FORMS ---------- */
function setupAuthForms() {
  const signin = document.getElementById('signinForm');
  if (signin) {
    signin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = signin.querySelector('#email').value.trim();
      const pw = signin.querySelector('#password').value;
      if (!email || !pw) return;

      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email, password: pw })
        });
        const data = await res.json();
        if (res.ok) {
          Auth.setUser({ email: email, name: data.name });
          window.location.href = 'index.html';
        } else {
          alert(data.detail || 'Invalid login');
        }
      } catch (err) {
        alert('Database connection failed. Please try again.');
      }
    });
  }
  const signup = document.getElementById('signupForm');
  if (signup) {
    signup.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = signup.querySelector('#name').value.trim();
      const email = signup.querySelector('#email').value.trim();
      const pw = signup.querySelector('#password').value;
      const confirm = signup.querySelector('#confirm').value;
      if (pw !== confirm) {
        alert('Passwords do not match!');
        return;
      }

      try {
        const res = await fetch('/api/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name, email: email, password: pw })
        });
        const data = await res.json();
        if (res.ok) {
          Auth.setUser({ email: email, name: name });
          alert('Account created successfully!');
          window.location.href = 'index.html';
        } else {
          alert(data.detail || 'Signup failed');
        }
      } catch (err) {
        alert('Database connection failed. Please try again.');
      }
    });
  }

  // Place Order
  const placeOrder = document.querySelector('[data-place-order]');
  if (placeOrder) {
    placeOrder.addEventListener('click', (e) => {
      e.preventDefault();
      Cart.clear();
      alert('🎉 Order placed successfully! Thank you for shopping with SimpliShop.');
      window.location.href = 'index.html';
    });
  }
}

/* ---------- INIT ---------- */
document.addEventListener('DOMContentLoaded', () => {
  refreshHeader();
  setupAccountMenu();
  setupPasswordToggle();
  setupSearchDropdown();
  setupAddToCart();
  setupQtySelectors();
  setupCompare();
  setupFilterAccordion();
  setupFilters();
  setupShippingOptions();
  setupPaymentOptions();
  setupAuthForms();
  renderCartIfPresent();
  renderCheckoutSummary();
});

document.addEventListener('cart:changed', () => {
  refreshHeader();
});

/* ---------- HERO CAROUSEL ---------- */
function setupCarousels() {
  document.querySelectorAll('[data-carousel]').forEach(el => {
    const track = el.querySelector('.carousel-track');
    const slides = el.querySelectorAll('.carousel-slide');
    const dots = el.querySelectorAll('.carousel-dot');
    const prev = el.querySelector('.carousel-prev');
    const next = el.querySelector('.carousel-next');
    const autoplayMs = parseInt(el.dataset.autoplay || '0', 10);

    if (!track || !slides.length) return;

    let current = 0;
    let timer = null;

    const goTo = (i) => {
      current = (i + slides.length) % slides.length;
      track.style.transform = `translateX(-${current * 100}%)`;
      dots.forEach((d, idx) => d.classList.toggle('active', idx === current));
      // Set dot color based on active slide background
      const active = slides[current];
      const isDark = active.classList.contains('slide-tech');
      dots.forEach(d => d.style.background = '');
      if (isDark) {
        dots.forEach((d, idx) => {
          if (!d.classList.contains('active')) d.style.background = 'rgba(255,255,255,0.40)';
        });
      }
    };
    const nextSlide = () => goTo(current + 1);
    const prevSlide = () => goTo(current - 1);

    const start = () => {
      if (autoplayMs > 0) {
        clearInterval(timer);
        timer = setInterval(nextSlide, autoplayMs);
      }
    };
    const stop = () => clearInterval(timer);

    if (prev) prev.addEventListener('click', () => { prevSlide(); start(); });
    if (next) next.addEventListener('click', () => { nextSlide(); start(); });
    dots.forEach((dot, idx) => {
      dot.addEventListener('click', () => { goTo(idx); start(); });
    });

    // Pause on hover
    el.addEventListener('mouseenter', stop);
    el.addEventListener('mouseleave', start);

    // Touch swipe (basic)
    let touchStart = 0;
    track.addEventListener('touchstart', (e) => { touchStart = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend', (e) => {
      const delta = e.changedTouches[0].clientX - touchStart;
      if (Math.abs(delta) > 50) {
        delta > 0 ? prevSlide() : nextSlide();
        start();
      }
    });

    goTo(0);
    start();
  });
}

/* ---------- PRODUCT DETAIL MODAL ---------- */
// Generic descriptions for products that don't have one in the markup
const PRODUCT_DESCRIPTIONS = {
  'p-laptop': "Powerful Dell XPS 15 with stunning FHD display, perfect for work and creative tasks. Intel i7 processor handles multitasking with ease.",
  'p-galaxy': "Samsung's flagship featuring a brilliant AMOLED display, 200MP camera, and 5G connectivity. Built-in S Pen included.",
  'p-camera': "Professional-grade Canon mirrorless system with 24-105mm versatile zoom lens. Capture stunning photos and 4K video.",
  'p-watch': "Stay connected and track your fitness with the latest Apple Watch. Always-on Retina display and advanced health sensors.",
  'p-ipad': 'Powerful M2 chip in a sleek 12.9" form factor. Perfect for creators, students, and professionals on the go.',
  'p-earbuds': "Affordable true wireless earbuds with charging case. Crisp audio, comfortable fit, and reliable Bluetooth connection.",
  'p-backpack': "Spacious 30L laptop backpack with water-resistant exterior. Padded compartments fit laptops up to 15.6 inches.",
  'p-press': "Premium 1L French press with thick borosilicate glass and stainless steel filter. Brews up to 8 cups of rich coffee.",
  'p-lamp': "Modern LED desk lamp with adjustable brightness and color temperature. Built-in USB charging port saves desk space.",
  'p-yoga': "Extra-thick 6mm yoga mat with non-slip dual-layer surface. Lightweight and easy to roll up for travel.",
  'p-shoes': "Lightweight running shoes with breathable mesh upper and responsive cushioning. Perfect for daily training.",
  'p-book': "Bestselling guide to behavioral finance and personal money psychology. Eye-opening insights on wealth and decision-making.",
  'p-sony': "Industry-leading noise cancellation with 30-hour battery life. Crystal-clear hands-free calls and intuitive controls.",
  'p-fitbit': "Track heart rate, sleep, stress, and over 40 exercise modes. Built-in GPS and 7-day battery life.",
  'p-coffee': "Automatic espresso maker compatible with Nespresso capsules. One-touch operation and energy-saving auto-off."
};

const GENERIC_FEATURES = [
  "Quality-tested by SimpliShop",
  "Free returns within 30 days",
  "Eligible for FREE delivery",
  "100% Purchase Protection"
];

function openProductModal(data) {
  let modal = document.querySelector('.product-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.className = 'product-modal';
    document.body.appendChild(modal);
  }

  const sub = data.priceStrike && data.priceStrike > data.price
    ? Math.round(((data.priceStrike - data.price) / data.priceStrike) * 100)
    : 0;

  const featuresHtml = (data.features && data.features.length)
    ? data.features.map(f => `<li>${escapeHtml(f)}</li>`).join('')
    : GENERIC_FEATURES.map(f => `<li>${escapeHtml(f)}</li>`).join('');

  modal.innerHTML = `
    <div class="product-modal-overlay"></div>
    <div class="product-modal-card">
      <button class="product-modal-close" aria-label="Close">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
      <div class="product-modal-body">
        <div class="product-modal-image">
          ${sub > 0 ? `<span class="discount-badge">-${sub}%</span>` : ''}
          ${data.image ? `<img src="${data.image}" alt="${escapeHtml(data.title)}" onerror="this.parentElement.classList.add('img-fallback');this.remove();">` : ''}
        </div>
        <div class="product-modal-info">
          <h2>${escapeHtml(data.title)}</h2>
          <div class="product-rating">
            <span class="stars">★★★★<span style="color:#ddd">★</span></span>
            <span class="rating-text">${escapeHtml(data.rating || '4.7')}</span>
            <span class="review-count">${escapeHtml(data.reviews || '(thousands of reviews)')}</span>
          </div>
          <div class="price-row">
            <span class="price">${peso(data.price)}</span>
            ${data.priceStrike ? `<span class="price-strike">${peso(data.priceStrike)}</span>` : ''}
            ${sub > 0 ? `<span class="save-tag">Save ${sub}%</span>` : ''}
          </div>
          <div class="free-delivery">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
            FREE delivery by Tomorrow
          </div>
          ${data.description ? `<p style="font-size:13px;color:var(--text-medium);margin-top:4px;">${escapeHtml(data.description)}</p>` : ''}
          <h4>About this item</h4>
          <ul class="feature-list">${featuresHtml}</ul>
          <div class="product-modal-actions">
            <div class="qty-selector" data-modal-qty>
              <button class="qty-minus" aria-label="Decrease">−</button>
              <input type="text" value="1" readonly>
              <button class="qty-plus" aria-label="Increase">+</button>
            </div>
            <button class="btn btn-primary" data-modal-add>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  modal.classList.add('active');

  const close = () => modal.classList.remove('active');
  modal.querySelector('.product-modal-overlay').addEventListener('click', close);
  modal.querySelector('.product-modal-close').addEventListener('click', close);
  document.addEventListener('keydown', function escListener(e) {
    if (e.key === 'Escape') {
      close();
      document.removeEventListener('keydown', escListener);
    }
  });

  // Wire qty selector
  const qtyEl = modal.querySelector('[data-modal-qty]');
  const input = qtyEl.querySelector('input');
  qtyEl.querySelector('.qty-minus').addEventListener('click', () => {
    const v = parseInt(input.value) || 1;
    if (v > 1) input.value = v - 1;
  });
  qtyEl.querySelector('.qty-plus').addEventListener('click', () => {
    const v = parseInt(input.value) || 1;
    input.value = v + 1;
  });

  // Wire add to cart
  modal.querySelector('[data-modal-add]').addEventListener('click', (e) => {
    const qty = parseInt(input.value) || 1;
    const product = {
      id: data.id,
      title: data.title,
      price: data.price,
      priceStrike: data.priceStrike,
      image: data.image
    };
    for (let i = 0; i < qty; i++) Cart.add(product);
    const btn = e.currentTarget;
    btn.classList.add('added');
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Added!';
    setTimeout(() => { close(); }, 800);
  });
}

function readProductFromCard(card) {
  // Read product data from a homepage product card
  const addBtn = card.querySelector('[data-add-to-cart]');
  if (!addBtn) return null;
  return {
    id: addBtn.dataset.id,
    title: addBtn.dataset.title,
    price: parseFloat(addBtn.dataset.price),
    priceStrike: addBtn.dataset.priceStrike ? parseFloat(addBtn.dataset.priceStrike) : null,
    image: addBtn.dataset.image,
    rating: card.querySelector('.rating-text')?.textContent.trim() || '4.7',
    reviews: card.querySelector('.review-count')?.textContent.trim() || '',
    description: PRODUCT_DESCRIPTIONS[addBtn.dataset.id] || null,
    features: null
  };
}

function readProductFromResult(item) {
  // Read product data from a search result item (has its own features list)
  const addBtn = item.querySelector('[data-add-to-cart]');
  if (!addBtn) return null;
  const features = Array.from(item.querySelectorAll('.result-features li')).map(li => li.textContent.trim());
  return {
    id: addBtn.dataset.id,
    title: addBtn.dataset.title,
    price: parseFloat(addBtn.dataset.price),
    priceStrike: addBtn.dataset.priceStrike ? parseFloat(addBtn.dataset.priceStrike) : null,
    image: addBtn.dataset.image,
    rating: item.querySelector('.rating-text')?.textContent.trim() || '4.7',
    reviews: item.querySelector('.review-count')?.textContent.trim() || '',
    description: null,
    features: features
  };
}

function setupProductModal() {
  // Make product cards clickable to open modal (homepage)
  document.querySelectorAll('.product-card').forEach(card => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', (e) => {
      // Don't trigger if user clicked the Add to Cart button
      if (e.target.closest('[data-add-to-cart]')) return;
      const data = readProductFromCard(card);
      if (data) openProductModal(data);
    });
  });

  // Wire "View Details" buttons on search result items
  document.querySelectorAll('.result-item').forEach(item => {
    const buttons = item.querySelectorAll('.result-actions .btn-outline');
    buttons.forEach(btn => {
      if (btn.textContent.trim().toLowerCase().includes('details')) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const data = readProductFromResult(item);
          if (data) openProductModal(data);
        });
      }
    });
  });
}

// Hook into existing init
document.addEventListener('DOMContentLoaded', () => {
  setupCarousels();
  setupProductModal();
});
