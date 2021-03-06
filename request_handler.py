from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from views.category_requests import create_category, get_all_categories, get_single_category, delete_category, update_category
from views.comment_requests import get_all_comments, get_single_comment, delete_comment, update_comment
from views.post_requests import get_all_posts, get_post_by_search, get_single_post, delete_post, create_post, update_post, get_post_by_user_id
from views.tag_requests import get_all_tags, get_single_tag, delete_tag, create_tag

from views.user import create_user, login_user


class HandleRequests(BaseHTTPRequestHandler):
    """Handles the requests to this server"""

    def parse_url(self, path):
        path_params = path.split("/")
        resource = path_params[1]

        # Add conditional statement that checks to see if ? and & are in resource
        # if "?" and "&" in resource:
        #     param = resource.split("?"[1])
        #     resource = resource.split("?")[0]
            # if they are, split up the url and return the strings as variables inside a tuple
        
        # Check if there is a query string parameter
        if "?" in resource:
            # GIVEN: /customers?email=jenna@solis.com

            param = resource.split("?")[1]  # email=jenna@solis.com
            resource = resource.split("?")[0]  # 'customers'
            pair = param.split("=")  # [ 'email', 'jenna@solis.com' ]
            key = pair[0]  # 'email'
            value = pair[1]  # 'jenna@solis.com'

            try:
                value = int(pair[1])
            except IndexError:
                pass  # No route parameter exists: /animals
            except ValueError:
                pass  # Request had trailing slash: /animals/
            return ( resource, key, value )

        # No query string parameter
        else:
            id = None

            try:
                id = int(path_params[2])
            except IndexError:
                pass  # No route parameter exists: /animals
            except ValueError:
                pass  # Request had trailing slash: /animals/

            return (resource, id)

    def _set_headers(self, status):
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        """Sets the OPTIONS headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def do_GET(self):
        self._set_headers(200)

        response = {}

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url(self.path)

        # Response from parse_url() is a tuple with 2
        # items in it, which means the request was for
        # `/animals` or `/animals/2`
        if len(parsed) == 2:
            ( resource, id ) = parsed

            if resource == "posts":
                if id is not None:
                    response = f"{get_single_post(id)}"
                else:
                    response = f"{get_all_posts()}"
            
            if resource == "categories":
                if id is not None:
                    response = f"{get_single_category(id)}"
                else:
                    response = f"{get_all_categories()}"
                    
            if resource == "tags":
                if id is not None:
                    response = f"{get_single_tag(id)}"
                else:
                    response = f"{get_all_tags()}"
            
            if resource == "comments":
                if id is not None:
                    response = f"{get_single_comment(id)}"
                else:
                    response = f"{get_all_comments()}"        
                            
        elif len(parsed) == 3:
            ( resource, key, value ) = parsed

            
            if key == "q" and resource == "posts":
                response = get_post_by_search(value)
                
            if key == "user_id" and resource == "posts":
                response = get_post_by_user_id(value)
            # if key == "expand" and resource == "posts":
            #     response = f"{get_all_posts(value)}"
                
        self.wfile.write(response.encode())


    def do_POST(self):
            """Make a post request to the server"""
            self._set_headers(201)
            content_len = int(self.headers.get('content-length', 0))
            post_body = json.loads(self.rfile.read(content_len))
            response = ''
            (resource, _) = self.parse_url(self.path)

            if resource == 'login':
                response = login_user(post_body)
            if resource == 'register':
                response = create_user(post_body)

            self.wfile.write(response.encode())
            
            new_post = None
            if resource == 'posts':
                new_post = create_post(post_body)
            self.wfile.write(f"{new_post}".encode())
            
            new_tag = None
            if resource == 'tags':
                new_tag = create_tag(post_body)
            self.wfile.write(f"{new_tag}".encode())

            new_category = None
            if resource == 'categories':
                new_category = create_category(post_body)
            self.wfile.write(f"{new_tag}".encode())


    def do_PUT(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        success = False

        if resource == "posts":
            success = update_post(id, post_body)
        
        if resource == "categories":
            success = update_category(id, post_body) 
            
        if resource == "comments":
            success = update_comment(id, post_body) 
        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

        self.wfile.write("".encode()) 

    def do_DELETE(self):
        # Set a 204 response code
        self._set_headers(204)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Delete a single animal from the list
        if resource == "posts":
            delete_post(id)
        
        if resource == "categories":
            delete_category(id)    
        
        if resource == "tags":
            delete_tag(id)
        
        if resource == "comments":
            delete_comment(id)          

        # Encode the new animal and send in response
        self.wfile.write("".encode())


def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
