package dev.grovarc.api

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class GrovarcApiApplication

fun main(args: Array<String>) {
    runApplication<GrovarcApiApplication>(*args)
}
