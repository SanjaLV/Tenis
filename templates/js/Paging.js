// {% comment %}
// Template Paging.js
//
// url -> url/?page=X
// page -> current page number
// max_page -> maximal page number
//
// HTML elements we may use
// page-menu - to place pages inside
// {% endcomment %}

const base_url = "/core{{url}}";

{% if page %}
const page = {{page}};
{% else %}
const page = 1;
{% endif %}
const max_page = {{max_page}};

function FirstPage() {
    MoveToPage(1 - page);
}

function LastPage() {
    MoveToPage(max_page - page);
}

function NextPage() {
    MoveToPage(+1);
}
function PrevPage() {
    MoveToPage(-1);
}
function GetMoveToPageParam(evt) {
    MoveToPage(evt.target.myparam);
}

function MoveToPage(offset) {
    let next_page = page + offset;
    if (next_page >= 1) {
        location.replace(base_url + "/?page=" + next_page.toString());
    }
}

function CreateLiWithDiv(is_active, on_click_function, text, param=null) {
    let li = document.createElement("li");
    li.classList.add("page-item");
    if (is_active) {
        li.classList.add("active");
    }
    let div = document.createElement("div");
    div.addEventListener("click", on_click_function, false);
    if (param != null) {
        div.myparam = param;
    }
    div.classList.add("page-link");
    div.innerText = text;
    li.appendChild(div);
    return li;
}

function max(a, b) {
    if (a > b) return a;
    return b;
}

function min(a, b) {
    if (a < b) return a;
    return b;
}

function Render() {
    let main = document.getElementById("page-menu");

    if (page !== 1) {
        main.appendChild(CreateLiWithDiv(false, FirstPage, "First"));
        main.appendChild(CreateLiWithDiv(false, PrevPage, "Previous"));
    }

    const count = 7;
    let l = -3;
    let r = +3;
    let max_left = 1 - page;
    let max_right = max_page - page;

    while (l + page <= 0) {
        l++;
        r++;
    }

    while (page + r > max_page) {
        l--;
        r--;
    }

    l = max(max_left, l);
    r = min(max_right, r);

    for (let i = l; i <= r; i++) {
        main.appendChild(CreateLiWithDiv(i === 0, GetMoveToPageParam, page + i, i));
    }

    if (page !== max_page) {
        main.appendChild(CreateLiWithDiv(false, NextPage, "Next"));
        main.appendChild(CreateLiWithDiv(false, LastPage, "Last"));
    }

}

window.onload = Render;
