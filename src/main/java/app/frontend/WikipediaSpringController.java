package app.frontend;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class WikipediaSpringController {


    @GetMapping("/api/query")
    public String query(@RequestParam String first,
                        @RequestParam String second) {
        return "You entered: " + first + " and " + second;
    }
    @GetMapping("/chuj")
    public String chuj(@RequestParam(defaultValue="") String chuj) {
        return chuj;
    }
}

