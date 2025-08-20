</div> <!-- End content area -->
    
    <!-- Footer Section -->
    <table cellpadding="0" cellspacing="0" width="771" border="0">
        <tr>
            <td bgcolor="#ffffff" colspan="4">
                <img height="3" alt="Policy of Liberty" align="center" src="images/white.gif" width="771" border="0">
            </td>
        </tr>
        <tr>
            <td bgcolor="#99cc99">
                <img height="20" alt="Policy of Liberty" src="images/end.gif" width="360" border="0" align="center">
            </td>
            <td bgcolor="#99cc99">
                <img height="20" alt="Policy of Liberty" align="center" src="images/backg.gif" width="27" border="0">
            </td>
            <td bgcolor="#99cc99">
                <img height="20" alt="Policy of Liberty" align="center" src="images/bottom.gif" width="318" border="0">
            </td>
            <td bgcolor="#99cc99">
                <a href="sindex.html" onmouseover="return true;" onmouseout="return true;">
                    <img height="20" alt="Policy of Liberty en Español" src="images/indnav_01.gif" width="66" border="0" name="indnav_01" align="center">
                </a>
            </td>
        </tr>
        <tr>
            <td bgcolor="#ffffff" colspan="4">
                <img height="3" alt="Policy of Liberty" align="center" src="images/white.gif" width="771" border="0">
            </td>
        </tr>
        <tr>
            <td bgcolor="#99cc99" colspan="4" height="15" width="771">
                <span class="foot">
                    &nbsp;&nbsp;&nbsp;
                    <a href="index.php" class="foot" title="Policy of Liberty Home">home</a> &nbsp;|&nbsp; 
                    <a href="freemarket.php" class="foot" title="Free Market Textbook">free market textbook</a> &nbsp;|&nbsp; 
                    <a href="books.php" class="foot" title="Public Policy Books">public policy books</a> &nbsp;|&nbsp; 
                    <a href="papers.php" class="foot" title="Articles and Papers">articles &amp; papers</a> &nbsp;|&nbsp; 
                    <a href="links.php" class="foot" title="Links">links</a> &nbsp;|&nbsp; 
                    <a href="quotes.php" class="foot" title="Quotes">quotes</a> &nbsp;|&nbsp; 
                    <a href="contact.php" class="foot" title="Contact Policy of Liberty">contact</a> &nbsp;|&nbsp; 
                    <a href="about.php" class="foot" title="About Dr. John Cobin">about me</a>
                </span>
            </td>
        </tr>
    </table>

    <!-- Contact Information Footer -->
    <div style="text-align: center; padding: 20px; background-color: #f5f5f5; border-top: 1px solid #cccccc;">
        <p style="margin: 0; font-size: 11px; color: #666666;">
            <strong>Dr. John M. Cobin</strong><br>
            José Suárez 185, Depto. 2, Viña del Mar, Chile 2541311<br>
            Phone/WhatsApp/Telegram: +56-949900391<br>
            Email: osorno7@earthlink.net | dinamico900@gmail.com<br>
            Website: <strong>www.policyofliberty.com</strong>
        </p>
        <p style="margin: 10px 0 0 0; font-size: 10px; color: #999999;">
            © <?php echo date('Y'); ?> Policy of Liberty. All rights reserved.
            | Non-fiction Writing, Editorial Services & Policy Analysis
        </p>
    </div>

</div> <!-- End container -->

<!-- JavaScript for enhanced functionality -->
<script type="text/javascript">
    // Simple image rollover function
    function changeImages(imgName, imgSrc) {
        if (document.images && document.images[imgName]) {
            document.images[imgName].src = imgSrc;
        }
    }
    
    // Ensure external links open in new window
    document.addEventListener('DOMContentLoaded', function() {
        var links = document.links;
        for (var i = 0; i < links.length; i++) {
            var link = links[i];
            if (link.hostname !== window.location.hostname) {
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
            }
        }
    });
    
    // Simple contact form validation (if contact forms are added)
    function validateEmail(email) {
        var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
</script>

<!-- Google Analytics or other tracking code can be added here -->

</body>
</html>