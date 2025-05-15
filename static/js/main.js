
import { getFirestore, collection, getDocs, query, orderBy } from 'firebase/firestore';

// Assuming Firebase is initialized elsewhere
const db = getFirestore();

//Manh
async function get_posts() {
    try {
        // Reference to the 'posts' collection
        const postsCollection = collection(db, 'posts');
        
        // Create a query to fetch posts, ordered by creation time (descending)
        const postsQuery = query(postsCollection, orderBy('createdAt', 'desc'));
        
        // Fetch all documents from the posts collection
        const querySnapshot = await getDocs(postsQuery);
        
        // Map the documents to an array of post objects
        const fetchedPosts = querySnapshot.docs.map(doc => ({
          id: doc.id, // Include the document ID
          ...doc.data() // Spread the post data (title, content, etc.)
        }));
        
        return fetchedPosts;
      } catch (error) {
        console.error('Error fetching posts:', error);
        throw error; // Rethrow the error for the caller to handle
      }
    }
    
    export default get_posts;


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
// let listings = [...fetchedListings];
let listings = get_posts();
let selectedListingId = null;

// Initialize the app
function init() {
    renderListings();
    setupEventListeners();
}

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
                <img src="${listing.image}" alt="${listing.title}">
                <h3>${listing.title}</h3>
                <p class="price">${listing.price}</p>
            </div>
        `;
        
        card.addEventListener('click', () => selectListing(listing.id));
        listingsContainer.appendChild(card);
    });
}

// Select a listing
function selectListing(id) {
    selectedListingId = id;
    const listing = listings.find(item => item.id === id);
    
    // Update UI
    renderListings(searchInput.value);
    showItemDetail(listing);
}

// Show item detail
function showItemDetail(listing) {
    // Hide other views
    emptyState.classList.add('hidden');
    newListingForm.classList.add('hidden');
    
    // Show detail view
    itemDetail.classList.remove('hidden');
    
    // Populate detail view
    itemDetail.innerHTML = `
        <div class="item-detail-header">
            <h2>${listing.title}</h2>
            <p class="price">${listing.price}</p>
        </div>
        
        <div class="item-detail-image">
            <img src="${listing.image}" alt="${listing.title}">
        </div>
        
        <div class="item-detail-info">
            <div>
                <h3>Mô tả</h3>
                <p>${listing.description}</p>
            </div>
            
            <div>
                <h3>Thông tin người bán</h3>
                <p>Người bán: ${listing.seller}</p>
                <p>Liên hệ: ${listing.contact}</p>
            </div>
        </div>
        
        <div class="item-detail-actions">
            <button class="btn btn-primary" onclick="window.location.href ='/payment'">Thanh toán ngay</button>
        </div>
    `;
}

// Show new listing form
function showNewListingForm() {
    // Reset selection
    selectedListingId = null;
    renderListings(searchInput.value);
    
    // Hide other views
    emptyState.classList.add('hidden');
    itemDetail.classList.add('hidden');
    
    // Show form
    newListingForm.classList.remove('hidden');
}

// Show empty state
function showEmptyState() {
    // Reset selection
    selectedListingId = null;
    renderListings(searchInput.value);
    
    // Hide other views
    itemDetail.classList.add('hidden');
    newListingForm.classList.add('hidden');
    
    // Show empty state
    emptyState.classList.remove('hidden');
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    searchInput.addEventListener('input', (e) => {
        renderListings(e.target.value);
    });
    
    // New listing buttons
    newListingBtn.addEventListener('click', showNewListingForm);
    emptyNewListingBtn.addEventListener('click', showNewListingForm);
    
    // Cancel button
    cancelBtn.addEventListener('click', () => {
        if (listings.length === 0) {
            showEmptyState();
        } else {
            showEmptyState();
        }
    });
    
    // Form submission
    listingForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form values
        const title = document.getElementById('title').value;
        const price = document.getElementById('price').value;
        const description = document.getElementById('description').value;
        const contact = document.getElementById('contact').value;
        
        // Create new listing
        const newListing = {
            id: Date.now(), // Use timestamp as ID
            title,
            price,
            description,
            image: 'https://via.placeholder.com/300x200',
            seller: 'Người dùng mới',
            contact
        };
        
        // Add to listings
        listings = [newListing, ...listings];
        
        // Reset form
        listingForm.reset();
        
        // Show the new listing
        renderListings(searchInput.value);
        selectListing(newListing.id);
    });
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);