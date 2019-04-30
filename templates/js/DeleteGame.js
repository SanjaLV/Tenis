function DeleteGame() {
    let x = confirm("Are you sure you want to delete?");
    if (x) {
        location.replace("/core/game/{{ game_id }}/delete");
    }
}