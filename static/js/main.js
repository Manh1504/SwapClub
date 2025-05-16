
import { getFirestore, collection, getDocs, query, orderBy } from 'firebase/firestore';

function init() {

}

function logout(){
    alert("Bạn có chắc chắn muốn đăng xuất không?");
    window.location.href="/login"
}

const initialListings = [];

// DOM Elements
const listingsContainer = document.getElementById('listings-container');
const detailContainer = document.getElementById('detail-container');
const emptyState = document.getElementById('empty-state');
const itemDetail = document.getElementById('item-detail');
const newListingForm = document.getElementById('new-listing-form');
const searchInput = document.getElementById('search-input');
const newListingBtn = document.getElementById('new-listing-btn');
const emptyNewListingBtn = document.getElementById('empty-new-listing-btn');
const cancelBtn = document.getElementById('cancel-btn');
const listingForm = document.getElementById('listing-form');

// Current state
let listings = [...initialListings];
let selectedListingId = null;

// Render listings
function renderListings(filterTerm = '') {
    listingsContainer.innerHTML = '';
    
    const filteredListings = filterTerm 
        ? listings.filter(listing => 
            listing.title.toLowerCase().includes(filterTerm.toLowerCase()) ||
            listing.description.toLowerCase().includes(filterTerm.toLowerCase())
          )
        : listings;
    
    if (filteredListings.length === 0) {
        listingsContainer.innerHTML = '<p class="no-results">Không tìm thấy kết quả phù hợp.</p>';
        return;
    }
    
    filteredListings.forEach(listing => {
        const isSelected = listing.id === selectedListingId;
        const card = document.createElement('div');
        card.className = `listing-card ${isSelected ? 'selected' : ''}`;
        card.dataset.id = listing.id;
        
        card.innerHTML = `
            <div class="listing-card-content">
                <h3>${listing.title}</h3>
                <img src="${listing.image}" alt="${listing.title}">
                <h4>${listing.description}</h4>
                <p class="price">${listing.price}</p>
            </div>
        `;
        
        card.addEventListener('click', () => selectListing(listing.id));
        listingsContainer.appendChild(card);
    });
}

/**
 * Hàm tạo bài viết mới
 * @param {string} header - Tiêu đề sản phẩm
 * @param {string|number} price - Giá
 * @param {string} description - Mô tả (tùy chọn)
 * @param {string} contact_info - Thông tin liên hệ
 * @param {File} image - File hình ảnh (tùy chọn)
 * @returns {Promise<Object>} Kết quả từ server
 */
const createPost = async (product_type, quantity, price, description = '', contact_info, image = null) => {
  try {
    // Tạo FormData
    const formData = new FormData();
    
    // Thêm các trường vào form
    formData.append('product_type', product_type);
    formData.append('quantity', quantity);
    formData.append('price', price);
    formData.append('description', description);
    formData.append('contact_info', contact_info);
    
    // Thêm hình ảnh nếu có
    if (image) {
      formData.append('image', image);
    }
    
    // Gửi request
    const response = await fetch('/post/create', {
      method: 'POST',
      body: formData
    });

    // Xử lý kết quả
    if (!response.ok) {
      throw new Error('Tạo bài viết thất bại');
    }

    const data = await response.json();
    return {
      success: true,
      data: data
    };
  } catch (error) {
    console.error('Lỗi:', error.message);
    return {
      success: false,
      message: error.message
    };
  }
};

const searchButton = document.createElement('button');
searchButton.textContent = 'Tìm kiếm';
searchInput.parentNode.insertBefore(searchButton, searchInput.nextSibling);

const searchResults = document.createElement('div');
searchResults.id = 'search-results';
searchInput.parentNode.insertBefore(searchResults, searchButton.nextSibling);

async function handleSearch() {
  const searchTerm = searchInput.value.trim();
  
  if (!searchTerm) {
    searchResults.innerHTML = '<p>Vui lòng nhập từ khóa</p>';
    return;
  }
  
  searchResults.innerHTML = '<p>Đang tìm kiếm...</p>';
  
  try {
    const response = await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: searchTerm })
    });
    
    if (!response.ok) throw new Error(`Lỗi: ${response.status}`);
    
    const data = await response.json();
    initialListings = data; // Lưu dữ liệu vào initialListings
    displaySearchResults(initialListings);
  } catch (error) {
    console.error('Lỗi tìm kiếm:', error);
    searchResults.innerHTML = `<p>Lỗi: ${error.message}</p>`;
  }
}

function displaySearchResults(data) {
  searchResults.innerHTML = '';
  
  if (!data || data.length === 0) {
    searchResults.innerHTML = '<p>Không tìm thấy kết quả</p>';
    return;
  }
  
  const resultList = document.createElement('ul');
  data.forEach(item => {
    const resultItem = document.createElement('li');
    resultItem.innerHTML = `
      <h3>${item.title || 'Không có tiêu đề'}</h3>
      <p>${item.description || 'Không có mô tả'}</p>
    `;
    resultList.appendChild(resultItem);
  });
  
  searchResults.appendChild(resultList);
}

searchButton.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') handleSearch();
});
