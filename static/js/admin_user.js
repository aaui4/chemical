function deleteUser(id){
    if(confirm("Are you sure you want to delete this user?")){
        fetch('/admin/delete_user/' + id, {
            method: 'DELETE'
        })
        .then(() => {
            location.reload();
        });
    }
}
