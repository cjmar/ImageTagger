var toggleFullSize = function(img_id)
{
    var img = document.getElementById(img_id);
    var full = img.getAttribute("data-toggle"); //Starts off as false
    if(full == "true")
    {
        img.className = "imgFit";
        img.setAttribute("data-toggle", "false");
    }
    else if(full == "false")
    {
        img.className = "imgCenterFit";
        img.setAttribute("data-toggle", "true");
    }
    console.log(img.getAttribute("data-toggle"));
};

var searchBar = function()
{
    var text = document.getElementById("searchbar").value;
    console.log("Searching: " + text);
    window.location.replace('/index?tags=' + text);
};

var imgView = (function()
{
    var fileList = [];      //List of file names in directory
    var currentPage = 0;    //The current page being represented
    var imgsOnPage = 20;    //How many images to show on a single page of the index
    var pageCount = 0;      //Totla number of pages

    var screenX = window.screen.width * window.devicePixelRatio;
    //var screenY = window.screen.height * windown.devicePixelRatio;
    var screenType;

        if(screenX < 540) { screenType = "small"; }
        else if(screenX < 720) { screenType = "medium"; }
        else { screenType = "large"; }

    console.log("Screen type is ", screenType);

    /*
        Adds the current list of file names to fileList
    */
    var setFileList = function(list_in)
    {
        //Represents the set of data currently working on
        fileList = list_in;
        //console.log(fileList.length + " total images and " + pageCount + " pages");
        //console.log(fileList);
        pageCount = Math.ceil(fileList.length / imgsOnPage) - 1;
    };

    /*
        Decrements current page to a minimum of 0
        Called by left arrow pagination
    */
    var prevPage = function()
    {
        currentPage--;
        if(currentPage < 0)
        {
            currentPage = 0;
        }
        showPage(currentPage);
    };

    /*
        Increments current page to a maximum of pageCount
        Called by right arrow pagination
    */
    var nextPage = function()
    {
        currentPage++;
        if(currentPage > pageCount)
        {
            currentPage = pageCount;
        }
        showPage(currentPage);
    };

    /*
        Populates index page based on the pageNum parameter
    */
    var showPage = function(pageNum)
    {

        currentPage = pageNum;

        var startIndex = currentPage * imgsOnPage;

        fillImages(startIndex);

        if(pageCount > 0)
        {
            createPagination();
        }
    };

    /*
        Populates index page with image links contained in cards
        Starts at fileList[index]
    */
    var fillImages = function(index)
    {   
        //Clear the parent div
        var contentDiv = document.getElementById("pictureList");
        contentDiv.innerHTML = "";

        var row = document.createElement("div");
        row.className = "row justify-content-center";
        for(var i = index; i < index + imgsOnPage && i < fileList.length; i++)
        {
            row.appendChild(createImgCard(i));
        }
        contentDiv.appendChild(row);
    };
    
    /*
        Creates an image card based on passed fileList[imgIndex]
    */
    var createImgCard = function(imgIndex)
    {
        var str = fileList[imgIndex];

        //Anchor tag to click on image and go to its viewer
        var picLink = document.createElement("a");
        picLink.href = "/image/" + str;

        //Image tag for display
        //TODO: Try and make this a thumbnail without caching a bunch of images in a file
        var picImg = document.createElement("img");
        picImg.className = "cardImg";
        picImg.src = "/getimage/" + str;
        picImg.alt = str;

        //Card div wrapper
        var picDiv = document.createElement("div");
        picDiv.className = "cardContainer";

        //Add everything together and return it
        picLink.appendChild(picImg);
        picDiv.appendChild(picLink);
        return picDiv;
    };

    /*
        Creates a paginated list
    */
    var createPagination = function()
    {
        var pageTop = document.getElementById("paginationTop"); //This is the div
        pageTop.innerHTML = "";

        var pageBot = document.getElementById("paginationBot"); //This is the div
        pageBot.innerHTML = "";

        //Add the left nav arrow
        pageTop.appendChild(createPageArrow("left"));
        pageBot.appendChild(createPageArrow("left"));

        //Add all the page numbers
        var pagesShown = pageCount;

        var pageStart = 0;
        var pageEnd = pagesShown;

        if(pageCount > 16) //How many pages are shown on paginated list
        {
            if(screenType == "small") { pagesShown = 8; }
            if(screenType == "medium") { pagesShown = 12; }
            else { pagesShown = 16; }
            pagesShown = 16;    //Maximum amount of pages shown in pagination
            pageEnd = pagesShown;
            pageStart = Math.max(currentPage - (pagesShown/2), 0);
            pageEnd = Math.min(pageStart + pagesShown, pageCount);
        }

        //Adds the page numbers to the pagination list
        var p = Math.min(pageStart, pageCount - pagesShown + 1);
        for(var i = 0; i < pagesShown; i++) //i = pageStart and i < pageEnd
        {
            
            pageTop.appendChild(createPageNumber(p));
            pageBot.appendChild(createPageNumber(p));
            if(p < pageEnd)
            {
                p++;
            }
            else
            {
                break;
            }
        }

        //Add the right nav arrow
        pageTop.appendChild(createPageArrow("right"));
        pageBot.appendChild(createPageArrow("right"));
    };

    var createPageArrow = function(side)
    {
        //Create the navigation arrows on the side
        var arrow = document.createElement("li");
        var anc = document.createElement("a");
        arrow.className = "page-item";
        anc.className = "page-link";
        anc.href="#";

        var tag;
        if(side === "left")
        {
            tag = "Previous";
            if(currentPage > 0)
            {
                arrow.addEventListener("click", function(){ imgView.prevPage(); }, false);
            }
        }
        if(side === "right")
        {
            tag = "Next";
            if(currentPage < pageCount)
            {
                arrow.addEventListener("click", function(){ imgView.nextPage(); }, false);
            }
        }

        anc.innerHTML = tag;
        arrow.appendChild(anc);

        return arrow;
    };

    var createPageNumber = function(num)
    {
        var itemLI = document.createElement("li");
        var itemA = document.createElement("a");
        itemLI.className = "page-item";
        itemA.className = "page-link";
        itemA.id = num;

        itemA.addEventListener("click", function(){ imgView.showPage(this.id); }, false);
        if(currentPage == num)
        {
            itemA.innerHTML = '<span style="text-decoration:underline;">' + num + '</span>';
        }
        else
        {
            itemA.innerHTML = num;
        }
        
        itemLI.appendChild(itemA);

        return itemLI;
    };

    return{
        setFileList:setFileList,
        showPage:showPage,
        nextPage:nextPage,
        prevPage:prevPage
    };
})();