/**
 * Blog Widget
 * Takes the settings from the CMS and creates the blog widget for use on any page
 * @author Alan Menhennet
 */
$.fn.blog = function() {
	var articles = [];
	var el = $(this.selector);
    var title = "";
    var readLabel = "";
    var settings = {};
    var date = new Date();

    // Get the JSON
    $.getJSON("/templateEngine-blog.js?v=" + date.getTime(), function(data){
        // Check if blog file isn't empty
        if(typeof data === "undefined"){
            throw new Error("Blog data was undefined");
        }
        
        // Check for articles
        if(typeof data.articles === "undefined"){
            throw new Error("Blog Articles were undefined");
        }
        
        // Check for blog button
        if(typeof data.readLabel === "undefined"){
            throw new Error("Blog Read Label was undefined");
        }
        
        // Check for blog heading
        if(typeof data.title === "undefined"){
            throw new Error("Blog Title was undefined");
        }
        
        // Check for blog settings
        if(typeof data.settings === "undefined"){
            throw new Error("Blog Settings were undefined");
        }
        
        // Set settings
        articles = data.articles;
        title = data.title;
        readLabel = data.readLabel;
        settings = data.settings;
        
        // Build the widget
        buildWidget();
    });

    /**
     * Create the widget HTML
     * then appends it to the target div
     */
    var buildWidget = function(){
        var html = '<div class="blog-widget">' + 
            '<div class="blog-widget-heading">' + title + '</div>';
        for(var i=0; i < articles.length; i++){
            html += getArticle(articles[i]);
        }
        html += "</div>";
        el.append(html);
    }
    
    /**
     * Get Article Html
     * @param  {Article} article [article]
     * @return {string}         [html for the article]
     */
    var getArticle = function(article){
        var html = '<div class="blog-widget-article">';
                        
        // If show hero image
        if(settings.showHeroImage){
            if(article.heroImage.filename.length > 0){
		 	    html += '<div class="blog-widget-article-img">'+
            	 		'<div class="blog-widget-article-imgFrame" style="background:url(\'/thumbnailsmall/' + article.heroImage.filename + '\'"></div>' +
	             	 '</div>';
            } else {
                html += '<div class="blog-widget-article-img noImage">'+
                        '<div class="blog-widget-article-imgFrame"></div>' +
                     '</div>';
            }
        }
        
        // Article Preview
		html += '<div class="blog-widget-article-preview">' +
                    '<div class="blog-widget-article-preview-title">' + article.title + '</div>';
        
        // Author
        if(settings.showAuthor){
            html += '<div class="blog-widget-article-author">' + article.author + '</div>';
        }

        // Date Time
        if(settings.showDate || settings.showTime){
            html += '<div class="blog-widget-article-date">';
            // Show Date
            if(settings.showDate){
                html += '<div class="blog-widget-article-date-date">' + article.date.date + '</div>';
            }
            // Show Date
            if(settings.showTime){
                html += '<div class="blog-widget-article-date-time">' + article.date.time + '</div>';
            }
            html += '</div>';
        }

        // Sub Heading
        if(settings.showSubHeading){
            html += '<div class="blog-widget-article-content-subheading">' + article.subheading + '</div>';
        }
        
        // Preview Text
        if(settings.showPreviewText){
            html += '<div class="blog-widget-article-content-text">' + article.preview + '</div>';
        }
  
        // Read more button
        html += '<a href="/blog/' + article.url + '" class="blog-widget-article-content-button">' + readLabel + '</a>' +
            '</div>' +
            '</div>';
        return html;
    }
    
};
