const modal = document.getElementById('galeriaModal');
  modal.addEventListener('show.bs.modal', function (event) {
    const trigger = event.relatedTarget;
    const index = trigger.getAttribute('data-bs-slide-to');
    const carousel = document.querySelector('#carouselGaleria');
    const bsCarousel = bootstrap.Carousel.getInstance(carousel) || new bootstrap.Carousel(carousel);
    bsCarousel.to(parseInt(index));
  });