function vote(type, id, value) {
    fetch(`/vote/${type}/${id}/${value}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        document.querySelector(`#${type}-${id}-votes`).textContent = data.votes;
    })
    .catch(error => console.error('Error:', error));
}
